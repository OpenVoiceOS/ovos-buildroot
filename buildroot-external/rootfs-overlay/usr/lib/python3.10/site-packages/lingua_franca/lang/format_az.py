# -*- coding: utf-8 -*-
#
# Copyright 2021 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime

from lingua_franca.lang.format_common import convert_to_mixed_fraction
from lingua_franca.lang.common_data_az import _NUM_STRING_AZ, _get_ordinal_ak, _get_daytime, \
    _FRACTION_STRING_AZ, _LONG_SCALE_AZ, _SHORT_SCALE_AZ, _SHORT_ORDINAL_AZ, _LONG_ORDINAL_AZ, \
    _get_full_time_ak, _get_half_time_ak


def nice_number_az(number, speech=True, denominators=range(1, 21)):
    """ Azerbaijani helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "4 yarım" for speech and "4 1/2" for text

    Args:
        number (int or float): the float to format
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """

    result = convert_to_mixed_fraction(number, denominators)
    if not result:
        # Give up, just represent as a 3 decimal number
        return str(round(number, 3))

    whole, num, den = result

    if not speech:
        if num == 0:
            # TODO: Number grouping?  E.g. "1,000,000"
            return str(whole)
        else:
            return '{} {}/{}'.format(whole, num, den)

    if num == 0:
        return str(whole)
    den_str = _FRACTION_STRING_AZ[den]
    if whole == 0:
        if den == 2:
            return 'yarım'
        return '{} {}'.format(den_str, num)
    if den == 2:
        return '{} yarım'.format(whole)
    return '{} və {} {}'.format(whole, den_str, num)

def pronounce_number_az(number, places=2, short_scale=True, scientific=False,
                        ordinals=False):
    """
    Convert a number to it's spoken equivalent

    For example, '5.2' would return 'beş nöqtə iki'

    Args:
        num(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
        short_scale (bool) : use short (True) or long scale (False)
            https://en.wikipedia.org/wiki/Names_of_large_numbers
        scientific (bool): pronounce in scientific notation
        ordinals (bool): pronounce in ordinal form "first" instead of "one"
    Returns:
        (str): The pronounced number
    """
    num = number
    # deal with infinity
    if num == float("inf"):
        return "sonsuzluq"
    elif num == float("-inf"):
        return "mənfi sonsuzluq"
    if scientific:
        number = '%E' % num
        n, power = number.replace("+", "").split("E")
        power = int(power)
        if power != 0:
            if ordinals:
                # This handles negatives of powers separately from the normal
                # handling since each call disables the scientific flag
                return '{}{} vurulsun on üstü {}{}'.format(
                    'mənfi ' if float(n) < 0 else '',
                    pronounce_number_az(
                        abs(float(n)), places, short_scale, False, ordinals=False),
                    'mənfi ' if power < 0 else '',
                    pronounce_number_az(abs(power), places, short_scale, False, ordinals=True))
            else:
                # This handles negatives of powers separately from the normal
                # handling since each call disables the scientific flag
                return '{}{} vurulsun on üstü {}{}'.format(
                    'mənfi ' if float(n) < 0 else '',
                    pronounce_number_az(
                        abs(float(n)), places, short_scale, False),
                    'mənfi ' if power < 0 else '',
                    pronounce_number_az(abs(power), places, short_scale, False))

    if short_scale:
        number_names = _NUM_STRING_AZ.copy()
        number_names.update(_SHORT_SCALE_AZ)
    else:
        number_names = _NUM_STRING_AZ.copy()
        number_names.update(_LONG_SCALE_AZ)

    digits = [number_names[n] for n in range(0, 20)]

    tens = [number_names[n] for n in range(10, 100, 10)]

    if short_scale:
        hundreds = [_SHORT_SCALE_AZ[n] for n in _SHORT_SCALE_AZ.keys()]
    else:
        hundreds = [_LONG_SCALE_AZ[n] for n in _LONG_SCALE_AZ.keys()]

    # deal with negatives
    result = ""
    if num < 0:
        # result = "mənfi " if scientific else "minus "
        result = "mənfi "
    num = abs(num)

    # check for a direct match
    if num in number_names and not ordinals:
        if num > 1000:
            result += "bir "
        result += number_names[num]
    else:
        def _sub_thousand(n, ordinals=False):
            assert 0 <= n <= 999
            if n in _SHORT_ORDINAL_AZ and ordinals:
                return _SHORT_ORDINAL_AZ[n]
            if n <= 19:
                return digits[n]
            elif n <= 99:
                q, r = divmod(n, 10)
                return tens[q - 1] + (" " + _sub_thousand(r, ordinals) if r
                                      else "")
            else:
                q, r = divmod(n, 100)
                return (digits[q] + " " if q != 1 else "") + "yüz" + (
                    " " + _sub_thousand(r, ordinals) if r else "")

        def _short_scale(n):
            if n >= 999*max(_SHORT_SCALE_AZ.keys()):
                return "sonsuzluq"
            ordi = ordinals

            if int(n) != n:
                ordi = False
            n = int(n)
            assert 0 <= n
            res = []
            for i, z in enumerate(_split_by(n, 1000)):
                if not z:
                    continue
                
                number = _sub_thousand(z, not i and ordi)

                if i:
                    if i >= len(hundreds):
                        return ""
                    number += " "
                    if ordi:

                        if i * 1000 in _SHORT_ORDINAL_AZ:
                            if z == 1:
                                number = _SHORT_ORDINAL_AZ[i * 1000]
                            else:
                                number += _SHORT_ORDINAL_AZ[i * 1000]
                        else:
                            if n not in _SHORT_SCALE_AZ:
                                num = int("1" + "0" * (len(str(n)) - 2))

                                number += _SHORT_SCALE_AZ[num] + _get_ordinal_ak(_SHORT_SCALE_AZ[num])
                            else:
                                number = _SHORT_SCALE_AZ[n] + _get_ordinal_ak(_SHORT_SCALE_AZ[n])
                    else:
                        number += hundreds[i]
                if number.startswith("bir min"):
                    number = number[4:]
                res.append(number)
                ordi = False

            return ", ".join(reversed(res))

        def _split_by(n, split=1000):
            assert 0 <= n
            res = []
            while n:
                n, r = divmod(n, split)
                res.append(r)
            return res

        def _long_scale(n):
            if n >= max(_LONG_SCALE_AZ.keys()):
                return "sonsuzluq"
            ordi = ordinals
            if int(n) != n:
                ordi = False
            n = int(n)
            assert 0 <= n
            res = []
            for i, z in enumerate(_split_by(n, 1000000)):
                if not z:
                    continue
                number = pronounce_number_az(z, places, True, scientific,
                                             ordinals=ordi and not i)
                # strip off the comma after the thousand
                if i:
                    if i >= len(hundreds):
                        return ""
                    # plus one as we skip 'thousand'
                    # (and 'hundred', but this is excluded by index value)
                    number = number.replace(',', '')

                    if ordi:
                        if i * 1000000 in _LONG_ORDINAL_AZ:
                            if z == 1:
                                number = _LONG_ORDINAL_AZ[
                                    (i + 1) * 1000000]
                            else:
                                number += _LONG_ORDINAL_AZ[
                                    (i + 1) * 1000000]
                        else:
                            if n not in _LONG_SCALE_AZ:
                                num = int("1" + "0" * (len(str(n)) - 2))

                                number += " " + _LONG_SCALE_AZ[
                                    num] + _get_ordinal_ak(_LONG_SCALE_AZ[num])
                            else:
                                number = " " + _LONG_SCALE_AZ[n] + _get_ordinal_ak(_LONG_SCALE_AZ[n])
                    else:

                        number += " " + hundreds[i + 1]
                res.append(number)
            return ", ".join(reversed(res))

        if short_scale:
            result += _short_scale(num)
        else:
            result += _long_scale(num)

    # deal with scientific notation unpronounceable as number
    if not result and "e" in str(num):
        return pronounce_number_az(num, places, short_scale, scientific=True)
    # Deal with fractional part
    elif not num == int(num) and places > 0:
        if abs(num) < 1.0 and (result == "mənfi " or not result):
            result += "sıfır"
        result += " nöqtə"
        _num_str = str(num)
        _num_str = _num_str.split(".")[1][0:places]
        for char in _num_str:
            result += " " + number_names[int(char)]
    return result

def nice_time_az(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
    For example, generate 'altının yarısı' for speech or '5:30' for
    text display.
    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M")
            if string[0] == '0':
                string = string[1:]  # strip leading zeros
            string = _get_daytime(dt.hour) + " " + string
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""

        # Either "0 8" or "13"
        if string[0] == '0':
            speak += pronounce_number_az(int(string[0])) + " "
            speak += pronounce_number_az(int(string[1]))
        else:
            speak = pronounce_number_az(int(string[0:2]))

        speak += " "
        if string[3] == '0':
            speak += pronounce_number_az(0) + " "
            speak += pronounce_number_az(int(string[4]))
        else:
            speak += pronounce_number_az(int(string[3:5]))
        return speak
    else:
        
        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        next_hour = (dt.hour + 1) % 12 or 12
        speak = ""
        if use_ampm:
            speak += _get_daytime(dt.hour) + " "

        if dt.minute == 0:
            speak += "{} tamamdır".format(pronounce_number_az(hour))
        elif dt.minute < 30:
            speak += "{}{} {} dəqiqə işləyib".format(pronounce_number_az(next_hour), _get_full_time_ak(next_hour),
                                                    pronounce_number_az(dt.minute))
        elif dt.minute == 30:
            speak += "{}{} yarısı".format(pronounce_number_az(next_hour), _get_half_time_ak(next_hour))
        else:
            speak += "{}{} {} dəqiqə qalıb".format(pronounce_number_az(next_hour), _get_full_time_ak(next_hour),
                                                  pronounce_number_az(dt.minute - 30))

        return speak

def nice_duration_az(duration, speech=True):
    """ Convert duration in seconds to a nice spoken timespan

    Examples:
       duration = 60  ->  "1:00" or "bir dəqiqə"
       duration = 163  ->  "2:43" or "iki deqiqe qırx üç saniyə"

    Args:
        duration: time, in seconds
        speech (bool): format for speech (True) or display (False)

    Returns:
        str: timespan as a string
    """

    if isinstance(duration, datetime.timedelta):
        duration = duration.total_seconds()

    # Do traditional rounding: 2.5->3, 3.5->4, plus this
    # helps in a few cases of where calculations generate
    # times like 2:59:59.9 instead of 3:00.
    duration += 0.5

    days = int(duration // 86400)
    hours = int(duration // 3600 % 24)
    minutes = int(duration // 60 % 60)
    seconds = int(duration % 60)

    if speech:
        out = ""
        if days > 0:
            out += pronounce_number_az(days) + " "
            out += "gün"
        if hours > 0:
            if out:
                out += " "
            out += pronounce_number_az(hours) + " "
            out += "saat"
        if minutes > 0:
            if out:
                out += " "
            out += pronounce_number_az(minutes) + " "
            out += "dəqiqə"
        if seconds > 0:
            if out:
                out += " "
            out += pronounce_number_az(seconds) + " "
            out += "saniyə"
    else:
        # M:SS, MM:SS, H:MM:SS, Dd H:MM:SS format
        out = ""
        if days > 0:
            out = str(days) + "g "
        if hours > 0 or days > 0:
            out += str(hours) + ":"
        if minutes < 10 and (hours > 0 or days > 0):
            out += "0"
        out += str(minutes) + ":"
        if seconds < 10:
            out += "0"
        out += str(seconds)

    return out