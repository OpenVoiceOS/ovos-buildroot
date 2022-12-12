#
# Copyright 2017 Mycroft AI Inc.
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
"""
Format functions for Euskara (eu-eu)

"""
from lingua_franca.lang.format_common import convert_to_mixed_fraction
from lingua_franca.time import to_local, now_local

HOUR_STRING_EU = {
    1: 'ordubata',
    2: 'ordubiak',
    3: 'hirurak',
    4: 'laurak',
    5: 'bostak',
    6: 'seirak',
    7: 'zazpirak',
    8: 'zortzirak',
    9: 'bederatziak',
    10: 'hamarrak',
    11: 'hamaikak',
    12: 'hamabiak'
}

NUM_STRING_EU = {
    0: 'zero',
    1: 'bat',
    2: 'bi',
    3: 'hiru',
    4: 'lau',
    5: 'bost',
    6: 'sei',
    7: 'zazpi',
    8: 'zortzi',
    9: 'bederatzi',
    10: 'hamar',
    11: 'hamaika',
    12: 'hamabi',
    13: 'hamahiru',
    14: 'hamalau',
    15: 'hamabost',
    16: 'hamasei',
    17: 'hamazazpi',
    18: 'hemezortzi',
    19: 'hemeretzi',
    20: 'hogei',
    30: 'hogeita hamar',
    40: 'berrogei',
    50: 'berrogeita hamar',
    60: 'hirurogei',
    70: 'hirurogehita hamar',
    80: 'laurogei',
    90: 'laurogeita hamar',
    100: 'ehun',
    200: 'berrehun',
    300: 'hirurehun',
    400: 'laurehun',
    500: 'bostehun',
    600: 'seirehun',
    700: 'zazpirehun',
    800: 'zortzirehun',
    900: 'bederatzirehun',
    1000: 'mila'
}

FRACTION_STRING_EU = {
    2: 'erdi',
    3: 'heren',
    4: 'laurden',
    5: 'bosten',
    6: 'seiren',
    7: 'zazpiren',
    8: 'zortziren',
    9: 'bederatziren',
    10: 'hamarren',
    11: 'hamaikaren',
    12: 'hamabiren',
    13: 'hamahiruren',
    14: 'hamalauren',
    15: 'hamabosten',
    16: 'hamaseiren',
    17: 'hamazazpiren',
    18: 'hemezortziren',
    19: 'hemeretziren',
    20: 'hogeiren'
}


def nice_number_eu(number, speech=True, denominators=range(1, 21)):
    """ Euskara helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "4 eta erdi" for speech and "4 1/2" for text

    Args:
        number (int or float): the float to format
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """
    strNumber = ""
    whole = 0
    num = 0
    den = 0

    result = convert_to_mixed_fraction(number, denominators)

    if not result:
        # Give up, just represent as a 3 decimal number
        whole = round(number, 3)
    else:
        whole, num, den = result

    if not speech:
        if num == 0:
            strNumber = '{:,}'.format(whole)
            strNumber = strNumber.replace(",", " ")
            strNumber = strNumber.replace(".", ",")
            return strNumber
        else:
            return '{} {}/{}'.format(whole, num, den)
    else:
        if num == 0:
            # if the number is not a fraction, nothing to do
            strNumber = str(whole)
            strNumber = strNumber.replace(".", ",")
            return strNumber
        den_str = FRACTION_STRING_EU[den]
        # if it is not an integer
        if whole == 0:
            # if there is no whole number
            if num == 1:
                # if numerator is 1, return "un medio", for example
                strNumber = '{} bat'.format(den_str)
            else:
                # else return "cuatro tercios", for example
                strNumber = '{} {}'.format(num, den_str)
        elif num == 1:
            # if there is a whole number and numerator is 1
            if den == 2:
                # if denominator is 2, return "1 y medio", for example
                strNumber = '{} eta {}'.format(whole, den_str)
            else:
                # else return "1 y 1 tercio", for example
                strNumber = '{} eta {} bat'.format(whole, den_str)
        else:
            # else return "2 y 3 cuarto", for example
            strNumber = '{} eta {} {}'.format(whole, num, den_str)

    return strNumber


def pronounce_number_eu(num, places=2):
    """
    Convert a number to it's spoken equivalent

    For example, '5.2' would return 'bost koma bi'

    Args:
        num(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
    Returns:
        (str): The pronounced number
    """
    if abs(num) >= 10000:
        # TODO: Soporta a números por encima de 1000
        return str(num)

    result = ""
    if num < 0:
        result = "minus "
    num = abs(num)

    thousands = int(num-int(num) % 1000)
    _num = num - thousands
    hundreds = int(_num-int(_num) % 100)
    _num = _num - hundreds
    tens = int(_num-_num % 10)
    ones = int(_num - tens)

    if thousands > 0:
        if thousands > 1000:
            result += NUM_STRING_EU[int(thousands/1000)] + ' '
        result += NUM_STRING_EU[1000]
        if hundreds > 0 and tens == 0 and ones == 0:
            result += ' eta '
        elif hundreds > 0 or tens > 0 or ones > 0:
            result += ' '
    if hundreds > 0:
        result +=  NUM_STRING_EU[hundreds]
        if tens > 0 or ones > 0:
            result += ' eta '
    if tens or ones:
        if tens == 0 or tens == 10 or ones == 0:
            result += NUM_STRING_EU[int(_num)]
        else:
            if (tens % 20) == 10:
                ones = ones + 10    
            result += NUM_STRING_EU[int(tens)].split(' ')[0].replace("ta", "")+str("ta ") + NUM_STRING_EU[int(ones)]
    if abs(num) < 1.0:
        result+= NUM_STRING_EU[0]
    # Deal with decimal part, in basque is commonly used the comma
    # instead the dot. Decimal part can be written both with comma
    # and dot, but when pronounced, its pronounced "koma"
    if not num == int(num) and places > 0:
        if abs(num) < 1.0 and (result == "minus " or not result):
            result += NUM_STRING_EU[0]
        result += " koma"
        _num_str = str(num)
        _num_str = _num_str.split(".")[1][0:places]
        for char in _num_str:
            result += " " + NUM_STRING_EU[int(char)]

    return result


def nice_time_eu(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'cinco treinta' for speech or '5:30' for
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
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    speak = ""
    if use_24hour:
        # Tenemos que tener en cuenta que cuando hablamos en formato
        # 24h, no hay que especificar ninguna precisión adicional
        # como "la noche", "la tarde" o "la mañana"
        # http://lema.rae.es/dpd/srv/search?id=YNoTWNJnAD6bhhVBf9
        speak += pronounce_number_eu(dt.hour) + 'ak'

        # las 14:04 son "las catorce cero cuatro"

        if dt.minute < 10:
            speak += " zero " + pronounce_number_eu(dt.minute)
        else:
            speak += " " + pronounce_number_eu(dt.minute)

    else:
        minute = dt.minute
        hour = dt.hour

        _hour = hour
        if _hour == 0:
            _hour = 12
        if _hour > 12:
            _hour -= 12

        if (minute > 30):
            _hour += 1

        speak = HOUR_STRING_EU[_hour]

        if minute != 0:
            if minute <= 30:
                if minute == 15:
                    speak += " eta laurden"
                elif minute == 30:
                    speak += " eta erdi"
                else:
                    speak += " eta " + pronounce_number_eu(minute)
            else:
                if minute == 45:
                    speak += " laurden gutxi"
                else:
                    speak += " " + pronounce_number_eu(60 - minute) + " gutxi"


        # si no especificamos de la tarde, noche, mañana, etc
        if minute == 0 and not use_ampm:
            # 3:00
            speak += " puntuan"

        if use_ampm:
            # "de la noche" es desde que anochece hasta medianoche
            # así que decir que es desde las 21h es algo subjetivo
            # en España a las 20h se dice "de la tarde"
            # en castellano, las 12h es de la mañana o mediodía
            # así que diremos "de la tarde" a partir de las 13h.
            # http://lema.rae.es/dpd/srv/search?id=YNoTWNJnAD6bhhVBf9
            if hour >= 6 and hour < 13:
                speak = "goizeko " + speak
            elif hour >= 13 and hour < 20:
                speak = "arratsaldeko " + speak
            else:
                speak = "gaueko " + speak
    return speak
    # hemen dago tranpa
    # return str(dt.hour) + ":" + str(dt.minute)

def nice_relative_time_eu(when, relative_to=None, lang=None):
    """Create a relative phrase to roughly describe a datetime

    Examples are "25 seconds", "tomorrow", "7 days".

    Args:
        when (datetime): Local timezone
        relative_to (datetime): Baseline for relative time, default is now()
        lang (str, optional): Defaults to "en-us".
    Returns:
        str: Relative description of the given time
    """
    if relative_to:
        now = relative_to
    else:
        now = now_local()
    delta = to_local(when) - now

    if delta.total_seconds() < 1:
        return "0 segundo"

    if delta.total_seconds() < 90:
        if delta.total_seconds() == 1:
            return "segundo bat"
        else:
            return "{} segundo".format(int(delta.total_seconds()))

    minutes = int((delta.total_seconds() + 30) // 60)  # +30 to round minutes
    if minutes < 90:
        if minutes == 1:
            return "minutu bat"
        else:
            return "{} minutu".format(minutes)

    hours = int((minutes + 30) // 60)  # +30 to round hours
    if hours < 36:
        if hours == 1:
            return "ordu bat"
        else:
            return "{} ordu".format(hours)

    # TODO: "2 weeks", "3 months", "4 years", etc
    days = int((hours + 12) // 24)  # +12 to round days
    if days == 1:
        return "egun bat"
    else:
        return "{} egun".format(days)
