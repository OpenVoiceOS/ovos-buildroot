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
    Parse functions for Basque (eu)
    TODO: numbers greater than 999999
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import gettz
from lingua_franca.lang.format_eu import pronounce_number_eu
from lingua_franca.lang.parse_common import *
from lingua_franca.lang.common_data_eu import _NUM_STRING_EU


def isFractional_eu(input_str):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        text (str): the string to check if fractional
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    if input_str.endswith('s', -1):
        input_str = input_str[:len(input_str) - 1]  # e.g. "fifths"

    aFrac = {"erdia": 2, "erdi": 2, "heren": 3, "laurden": 4,
             "laurdena": 4, "bosten": 5, "bostena": 5, "seiren": 6, "seirena": 6,
             "zazpiren": 7, "zapirena": 7, "zortziren": 8, "zortzirena": 8,
             "bederatziren": 9, "bederatzirena": 9, "hamarren": 10, "hamarrena": 10,
             "hamaikaren": 11, "hamaikarena": 11, "hamabiren": 12, "hamabirena": 12}

    if input_str.lower() in aFrac:
        return 1.0 / aFrac[input_str]
    if (input_str == "hogeiren" or input_str == "hogeirena"):
        return 1.0 / 20
    if (input_str == "hogeita hamarren" or input_str == "hogeita hamarrena"):
        return 1.0 / 30
    if (input_str == "ehunen" or input_str == "ehunena"):
        return 1.0 / 100
    if (input_str == "milaren" or input_str == "milarena"):
        return 1.0 / 1000
    return False


# TODO: short_scale and ordinals don't do anything here.
# The parameters are present in the function signature for API compatibility
# reasons.
#
# Returns incorrect output on certain fractional phrases like, "cuarto de dos"
def extract_number_eu(text, short_scale=True, ordinals=False):
    """
    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.
    Args:
        text (str): the string to normalize
    Returns:
        (int) or (float): The value of extracted number

    """
    aWords = text.lower().split()
    count = 0
    result = None
    while count < len(aWords):
        val = 0
        word = aWords[count]
        next_next_word = None
        if count + 1 < len(aWords):
            next_word = aWords[count + 1]
            if count + 2 < len(aWords):
                next_next_word = aWords[count + 2]
        else:
            next_word = None

        # is current word a number?
        if word in _NUM_STRING_EU:
            val = _NUM_STRING_EU[word]
        elif word.isdigit():  # doesn't work with decimals
            val = int(word)
        elif is_numeric(word):
            val = float(word)
        elif isFractional_eu(word):
            if next_word in _NUM_STRING_EU:
                # erdi bat, heren bat, etab
                result = _NUM_STRING_EU[next_word]
                # hurrengo hitza (bat, bi, ...) salto egin 
                next_word = None
                count += 2
            elif not result:
                result = 1
                count += 1
            result = result * isFractional_eu(word)
            continue

        if not val:
            # look for fractions like "2/3"
            aPieces = word.split('/')
            # if (len(aPieces) == 2 and is_numeric(aPieces[0])
            #   and is_numeric(aPieces[1])):
            if look_for_fractions(aPieces):
                val = float(aPieces[0]) / float(aPieces[1])

        if val:
            if result is None:
                result = 0
            # handle fractions
            if next_word == "en" or next_word == "ren":
                result = float(result) / float(val)
            else:
                result = val

        if next_word is None:
            break

        # number word and fraction
        ands = ["eta"]
        if next_word in ands:
            zeros = 0
            if result is None:
                count += 1
                continue
            newWords = aWords[count + 2:]
            newText = ""
            for word in newWords:
                newText += word + " "

            afterAndVal = extract_number_eu(newText[:-1])
            if afterAndVal:
                if result < afterAndVal or result < 20:
                    while afterAndVal > 1:
                        afterAndVal = afterAndVal / 10.0
                    for word in newWords:
                        if word == "zero" or word == "0":
                            zeros += 1
                        else:
                            break
                for _ in range(0, zeros):
                    afterAndVal = afterAndVal / 10.0
                result += afterAndVal
                break
        elif next_next_word is not None:
            if next_next_word in ands:
                newWords = aWords[count + 3:]
                newText = ""
                for word in newWords:
                    newText += word + " "
                afterAndVal = extract_number_eu(newText[:-1])
                if afterAndVal:
                    if result is None:
                        result = 0
                    result += afterAndVal
                    break

        decimals = ["puntu", "koma", ".", ","]
        if next_word in decimals:
            zeros = 0
            newWords = aWords[count + 2:]
            newText = ""
            for word in newWords:
                newText += word + " "
            for word in newWords:
                if word == "zero" or word == "0":
                    zeros += 1
                else:
                    break
            afterDotVal = str(extract_number_eu(newText[:-1]))
            afterDotVal = zeros * "0" + afterDotVal
            result = float(str(result) + "." + afterDotVal)
            break
        count += 1

    # Return the $str with the number related words removed
    # (now empty strings, so strlen == 0)
    # aWords = [word for word in aWords if len(word) > 0]
    # text = ' '.join(aWords)
    if "." in str(result):
        integer, dec = str(result).split(".")
        # cast float to int
        if dec == "0":
            result = int(integer)

    return result or False


# TODO Not parsing 'cero'
def eu_number_parse(words, i):
    def eu_cte(i, s):
        if i < len(words) and s == words[i]:
            return s, i + 1
        return None

    def eu_number_word(i, mi, ma):
        if i < len(words):
            v = _NUM_STRING_EU.get(words[i])
            if v and v >= mi and v <= ma:
                return v, i + 1
        return None

    def eu_number_1_99(i):
        if i >= len(words):
            return None
        r1 = eu_number_word(i, 1, 29)
        if r1:
            return r1

        composed = False
        if  words[i] != "eta" and words[i][-2:] == "ta":
            composed = True
            words[i] = words[i][:-2]

        r1 = eu_number_word(i, 20, 90)

        if r1:
            v1, i1 = r1

            if composed:
                # i2 = r2[1]
                r3 = eu_number_word(i1, 1, 19)
                if r3:
                    v3, i3 = r3
                    return v1 + v3, i3
            return r1
        return None

    def eu_number_1_999(i):
        r1 = eu_number_word(i, 100, 900)
        if r1:
            v1, i1 = r1
            r2 = eu_cte(i1, "eta")
            if r2:
                i2 = r2[1]
                r3 = eu_number_1_99(i2)
                if r3:
                    v3, i3 = r3
                    return v1 + v3, i3
            else:
                return r1

        # [1-99]
        r1 = eu_number_1_99(i)
        if r1:
            return r1

        return None

    def eu_number(i):
        # check for cero
        r1 = eu_number_word(i, 0, 0)
        if r1:
            return r1

        # check for [1-999] (mil [0-999])?
        r1 = eu_number_1_999(i)
        if r1:
            v1, i1 = r1
            r2 = eu_cte(i1, "mila")
            if r2:
                i2 = r2[1]
                r3 = eu_number_1_999(i2)
                if r3:
                    v3, i3 = r3
                    return v1 * 1000 + v3, i3
                else:
                    return v1 * 1000, i2
            else:
                return r1
        return None

    return eu_number(i)


def extract_numbers_eu(text, short_scale=True, ordinals=False):
    """
        Takes in a string and extracts a list of numbers.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
    Returns:
        list: list of extracted numbers as floats
    """
    return extract_numbers_generic(text, pronounce_number_eu, extract_number_eu,
                                   short_scale=short_scale, ordinals=ordinals)


def normalize_eu(text, remove_articles=True):
    """ Basque string normalization """

    words = text.split()  # this also removed extra spaces
    normalized = ""
    i = 0
    while i < len(words):
        word = words[i]
        # Convert numbers into digits
        r = eu_number_parse(words, i)
        if r:
            v, i = r
            normalized += " " + str(v)
            continue

        normalized += " " + word
        i += 1

    return normalized[1:]  # strip the initial space
    return text


# TODO MycroftAI/mycroft-core#2348
def extract_datetime_eu(input_str, anchorDate=None, default_time=None):
    def clean_string(s):
        # cleans the input string of unneeded punctuation and capitalization
        # among other things
        symbols = [".", ",", ";", "?", "!", "."]
        # noise_words = ["entre", "la", "del", "al", "el", "de",
        #                "para", "una", "cualquier", "a",
        #                "e'", "esta", "este"]
        # TODO
        noise_words = ["artean", "tartean", "edozein", "hau", "hontan", "honetan",
                       "para", "una", "cualquier", "a",
                       "e'", "esta", "este"]

        for word in symbols:
            s = s.replace(word, "")
        for word in noise_words:
            s = s.replace(" " + word + " ", " ")
        s = s.lower().replace(
            "-",
            " ").replace(
            "_",
            "")
        # handle synonyms and equivalents, "tomorrow early = tomorrow morning
        synonyms = {"goiza": ["egunsentia", "goiz", "oso goiz"],
                    "arratsaldea": ["arratsa", "bazkalostea", "arratsalde", "arrats"],
                    "gaua": ["iluntzea", "berandu", "gau", "gaba"]}
        for syn in synonyms:
            for word in synonyms[syn]:
                s = s.replace(" " + word + " ", " " + syn + " ")
        # relevant plurals
        wordlist = ["goizak", "arratsaldeak", "gauak", "egunak", "asteak",
                    "urteak", "minutuak", "segunduak", "hurrengoak",
                    "datozenak", "orduak", "hilabeteak"]
        for _, word in enumerate(wordlist):
            s = s.replace(word, word.rstrip('ak'))
        # s = s.replace("meses", "mes").replace("anteriores", "anterior")
        return s

    def date_found():
        return found or \
            (
                datestr != "" or
                yearOffset != 0 or monthOffset != 0 or
                dayOffset is True or hrOffset != 0 or
                hrAbs or minOffset != 0 or
                minAbs or secOffset != 0
            )

    if input_str == "":
        return None
    if anchorDate is None:
        anchorDate = datetime.now()

    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    dateNow = anchorDate
    today = dateNow.strftime("%w")
    currentYear = dateNow.strftime("%Y")
    fromFlag = False
    datestr = ""
    hasYear = False
    timeQualifier = ""

    words = clean_string(input_str).split(" ")
    timeQualifiersList = ['goiza', 'arratsaldea', 'gaua']
    time_indicators = ["en", "la", "al", "por", "pasados",
                       "pasadas", "día", "hora"]
    days = ['astelehena', 'asteartea', 'asteazkena',
            'osteguna', 'ostirala', 'larunbata', 'igandea']
    months = ['urtarrila', 'otsaila', 'martxoa', 'apirila', 'maiatza', 'ekaina',
              'uztaila', 'abuztua', 'iraila', 'urria', 'azaroa',
              'abendua']
    monthsShort = ['urt', 'ots', 'mar', 'api', 'mai', 'eka', 'uzt', 'abu',
                   'ira', 'urr', 'aza', 'abe']
    nexts = ["hurrengo", "datorren", "ondorengo"]
    suffix_nexts = ["barru"]
    lasts = ["azken", "duela"]
    suffix_lasts = ["aurreko"]
    nxts = ["ondorengo", "hurrengo", "datorren"]
    prevs = ["aurreko", "duela", "previo", "anterior"]
    #  TODO
    froms = ["desde", "en", "para", "después de", "por", "próximo",
             "próxima", "de"]
    thises = ["hau"]
    froms += thises
    lists = nxts + prevs + froms + time_indicators
    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""

        start = idx
        used = 0
        # save timequalifier for later
        if word in timeQualifiersList:
            timeQualifier = word

        # parse today, tomorrow, yesterday
        elif (word == "gaur" or word == "gaurko") and not fromFlag:
            dayOffset = 0
            used += 1
        elif (word == "bihar" or word == "biharko") and not fromFlag:
            dayOffset = 1
            used += 1
        elif (word == "atzo" or word == "atzoko") and not fromFlag:
            dayOffset -= 1
            used += 1
        # before yesterday
        elif (word == "herenegun" or word == "herenegungo") and not fromFlag:
            dayOffset -= 2
            used += 1
            # if wordNext == "ayer":
            #     used += 1
        # elif word == "ante" and wordNext == "ante" and wordNextNext == \
        #         "ayer" and not fromFlag:
        #     dayOffset -= 3
        #     used += 3
        # elif word == "ante anteayer" and not fromFlag:
        #     dayOffset -= 3
        #     used += 1
        # day after tomorrow
        elif (word == "etzi" or word == "etziko") and not fromFlag:
            dayOffset += 2
            used = 1
        elif (word == "etzidamu" or word == "etzidamuko") and not fromFlag:
            dayOffset += 3
            used = 1
        # parse 5 days, 10 weeks, last week, next week, week after
        elif word == "egun" or word == "eguna" or word == "eguneko":
            if wordPrevPrev and wordPrevPrev == "duela":
                used += 1
                if wordPrev and wordPrev[0].isdigit():
                    dayOffset -= int(wordPrev)
                    start -= 1
                    used += 1
            elif (wordPrev and wordPrev[0].isdigit() and
                  wordNext not in months and
                  wordNext not in monthsShort):
                dayOffset += int(wordPrev)
                start -= 1
                used += 2
            elif wordNext and wordNext[0].isdigit() and wordNextNext not in \
                    months and wordNextNext not in monthsShort:
                dayOffset += int(wordNext)
                start -= 1
                used += 2

        elif word == "aste" or word == "astea" or word == "asteko" and not fromFlag:
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev) * 7
                start -= 1
                used = 2
            for w in nexts:
                if wordPrev == w:
                    dayOffset = 7
                    start -= 1
                    used = 2
            for w in lasts:
                if wordPrev == w:
                    dayOffset = -7
                    start -= 1
                    used = 2
            for w in suffix_nexts:
                if wordNext == w:
                    dayOffset = 7
                    start -= 1
                    used = 2
            for w in suffix_lasts:
                if wordNext == w:
                    dayOffset = -7
                    start -= 1
                    used = 2
        # parse 10 months, next month, last month
        elif word == "hilabete" or word == "hilabetea" or word == "hilabeteko" and not fromFlag:
            if wordPrev[0].isdigit():
                monthOffset = int(wordPrev)
                start -= 1
                used = 2
            for w in nexts:
                if wordPrev == w:
                    monthOffset = 7
                    start -= 1
                    used = 2
            for w in lasts:
                if wordPrev == w:
                    monthOffset = -7
                    start -= 1
                    used = 2
            for w in suffix_nexts:
                if wordNext == w:
                    monthOffset = 7
                    start -= 1
                    used = 2
            for w in suffix_lasts:
                if wordNext == w:
                    monthOffset = -7
                    start -= 1
                    used = 2
        # parse 5 years, next year, last year
        elif word == "urte" or word == "urtea" or word == "urteko" and not fromFlag:
            if wordPrev[0].isdigit():
                yearOffset = int(wordPrev)
                start -= 1
                used = 2
            for w in nexts:
                if wordPrev == w:
                    yearOffset = 1
                    start -= 1
                    used = 2
            for w in lasts:
                if wordPrev == w:
                    yearOffset = -1
                    start -= 1
                    used = 2
            for w in suffix_nexts:
                if wordNext == w:
                    yearOffset = 1
                    start -= 1
                    used = 2
            for w in suffix_lasts:
                if wordNext == w:
                    yearOffset = -1
                    start -= 1
                    used = 2
        # parse Monday, Tuesday, etc., and next Monday,
        # last Tuesday, etc.
        elif word in days and not fromFlag:
            d = days.index(word)
            dayOffset = (d + 1) - int(today)
            used = 1
            if dayOffset < 0:
                dayOffset += 7
            if wordPrev == "hurrengo":
                dayOffset += 7
                used += 1
                start -= 1
            elif wordPrev == "aurreko":
                dayOffset -= 7
                used += 1
                start -= 1
            if wordNext == "hurrengo":
                # dayOffset += 7
                used += 1
            elif wordNext == "aurreko":
                # dayOffset -= 7
                used += 1
        # parse 15 of July, June 20th, Feb 18, 19 of February
        elif word in months or word in monthsShort:
            try:
                m = months.index(word)
            except ValueError:
                m = monthsShort.index(word)
            used += 1
            datestr = months[m]
            if wordPrev and wordPrev[0].isdigit():
                # 13 mayo
                datestr += " " + wordPrev
                start -= 1
                used += 1
                if wordNext and wordNext[0].isdigit():
                    datestr += " " + wordNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordNext and wordNext[0].isdigit():
                # mayo 13
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordPrevPrev and wordPrevPrev[0].isdigit():
                # 13 dia mayo
                datestr += " " + wordPrevPrev

                start -= 2
                used += 2
                if wordNext and word[0].isdigit():
                    datestr += " " + wordNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordNextNext and wordNextNext[0].isdigit():
                # mayo dia 13
                datestr += " " + wordNextNext
                used += 2
                if wordNextNextNext and wordNextNextNext[0].isdigit():
                    datestr += " " + wordNextNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            if datestr in months:
                datestr = ""

        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July
        validFollowups = days + months + monthsShort
        validFollowups.append("gaur")
        validFollowups.append("bihar")
        validFollowups.append("atzo")
        # validFollowups.append("atzoko")
        validFollowups.append("herenegun")
        validFollowups.append("orain")
        validFollowups.append("oraintxe")
        # validFollowups.append("ante")

        # TODO
        if word in froms and wordNext in validFollowups:

            if not (word == "bihar" or word == "herenegun" or word == "atzo"):
                used = 1
                fromFlag = True
            if wordNext == "bihar":
                dayOffset += 1
            elif wordNext == "atzo" or wordNext == "atzoko":
                dayOffset -= 1
            elif wordNext == "herenegun":
                dayOffset -= 2
            # elif (wordNext == "ante" and wordNext == "ante" and
            #       wordNextNextNext == "ayer"):
            #     dayOffset -= 3
            elif wordNext in days:
                d = days.index(wordNext)
                tmpOffset = (d + 1) - int(today)
                used = 2
                # if wordNextNext == "feira":
                #     used += 1
                if tmpOffset < 0:
                    tmpOffset += 7
                if wordNextNext:
                    if wordNextNext in nxts:
                        tmpOffset += 7
                        used += 1
                    elif wordNextNext in prevs:
                        tmpOffset -= 7
                        used += 1
                dayOffset += tmpOffset
            elif wordNextNext and wordNextNext in days:
                d = days.index(wordNextNext)
                tmpOffset = (d + 1) - int(today)
                used = 3
                if wordNextNextNext:
                    if wordNextNextNext in nxts:
                        tmpOffset += 7
                        used += 1
                    elif wordNextNextNext in prevs:
                        tmpOffset -= 7
                        used += 1
                dayOffset += tmpOffset
                # if wordNextNextNext == "feira":
                #     used += 1
        if wordNext in months:
            used -= 1
        if used > 0:
            if start - 1 > 0 and words[start - 1] in lists:
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in lists:
                words[start - 1] = ""
            found = True
            daySpecified = True

    # parse time
    hrOffset = 0
    minOffset = 0
    secOffset = 0
    hrAbs = None
    minAbs = None

    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""
        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word == "eguerdi" or word == "eguerdia" or word == "eguerdian":
            hrAbs = 12
            used += 2
        elif word == "gauerdi" or word == "gauerdia" or word == "gauerdian":
            hrAbs = 0
            used += 2
        elif word == "goiza":
            if not hrAbs:
                hrAbs = 8
            used += 1
        elif word == "arratsaldea" or word == "arratsa" or word == "arratsean" or word == "arratsaldean":
            if not hrAbs:
                hrAbs = 15
            used += 1
        # TODO
        # elif word == "media" and wordNext == "tarde":
        #     if not hrAbs:
        #         hrAbs = 17
        #     used += 2
        elif word == "iluntze" or word == "iluntzea" or word == "iluntzean":
            if not hrAbs:
                hrAbs = 20
            used += 2
        # TODO
        # elif word == "media" and wordNext == "mañana":
        #     if not hrAbs:
        #         hrAbs = 10
        #     used += 2
        # elif word == "fim" and wordNext == "tarde":
        #     if not hrAbs:
        #         hrAbs = 19
        #     used += 2
        elif word == "egunsentia" or word == "egunsentian" or word == "egunsenti":
            if not hrAbs:
                hrAbs = 6
            used += 1
        # elif word == "madrugada":
        #     if not hrAbs:
        #         hrAbs = 1
        #     used += 2
        elif word == "gaua" or word == "gauean" or word == "gau":
            if not hrAbs:
                hrAbs = 21
            used += 1
        # parse half an hour, quarter hour
        # TODO
        elif (word == "hora" and
                (wordPrev in time_indicators or wordPrevPrev in
                 time_indicators)):
            if wordPrev == "media":
                minOffset = 30
            elif wordPrev == "cuarto":
                minOffset = 15
            elif wordPrevPrev == "cuarto":
                minOffset = 15
                if idx > 2 and words[idx - 3] in time_indicators:
                    words[idx - 3] = ""
                words[idx - 2] = ""
            else:
                hrOffset = 1
            if wordPrevPrev in time_indicators:
                words[idx - 2] = ""
            words[idx - 1] = ""
            used += 1
            hrAbs = -1
            minAbs = -1
        # parse 5:00 am, 12:00 p.m., etc
        elif word[0].isdigit():
            isTime = True
            strHH = ""
            strMM = ""
            remainder = ""
            if ':' in word:
                # parse colons
                # "3:00 in the morning"
                stage = 0
                length = len(word)
                for i in range(length):
                    if stage == 0:
                        if word[i].isdigit():
                            strHH += word[i]
                        elif word[i] == ":":
                            stage = 1
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 1:
                        if word[i].isdigit():
                            strMM += word[i]
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 2:
                        remainder = word[i:].replace(".", "")
                        break
                if remainder == "":
                    nextWord = wordNext.replace(".", "")
                    if nextWord == "am" or nextWord == "pm":
                        remainder = nextWord
                        used += 1
                    elif wordNext == "goiza" or wordNext == "egunsentia" or wordNext == "goizeko" or wordNext == "egunsentiko":
                        remainder = "am"
                        used += 1
                    elif wordPrev == "arratsaldeko" or wordPrev == "arratsaldea" or wordPrev == "arratsaldean":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "gaua" or wordNext == "gauean" or wordNext == "gaueko":
                        if 0 < int(word[0]) < 6:
                            remainder = "am"
                        else:
                            remainder = "pm"
                        used += 1
                    elif wordNext in thises and (wordNextNext == "goiza" or wordNextNext == "goizean" or wordNextNext == "goizeko"):
                        remainder = "am"
                        used = 2
                    elif wordNext in thises and \
                        (wordNextNext == "arratsaldea" or wordNextNext == "arratsaldean" or wordNextNext == "arratsaldeko"):
                        remainder = "pm"
                        used = 2
                    elif wordNext in thises and (wordNextNext == "gaua" or wordNextNext == "gauean" or wordNextNext == "gaueko"):
                        remainder = "pm"
                        used = 2
                    else:
                        if timeQualifier != "":
                            if strHH <= 12 and \
                                    (timeQualifier == "goiza" or
                                     timeQualifier == "arratsaldea"):
                                strHH += 12

            else:
                # try to parse # s without colons
                # 5 hours, 10 minutes etc.
                length = len(word)
                strNum = ""
                remainder = ""
                for i in range(length):
                    if word[i].isdigit():
                        strNum += word[i]
                    else:
                        remainder += word[i]

                if remainder == "":
                    remainder = wordNext.replace(".", "").lstrip().rstrip()

                if (
                        remainder == "pm" or
                        wordNext == "pm" or
                        remainder == "p.m." or
                        wordNext == "p.m."):
                    strHH = strNum
                    remainder = "pm"
                    used = 1
                elif (
                        remainder == "am" or
                        wordNext == "am" or
                        remainder == "a.m." or
                        wordNext == "a.m."):
                    strHH = strNum
                    remainder = "am"
                    used = 1
                else:
                    if (wordNext == "pm" or
                            wordNext == "p.m." or
                            wordPrev == "arratsaldeko"):
                        strHH = strNum
                        remainder = "pm"
                        used = 0
                    elif (wordNext == "am" or
                          wordNext == "a.m." or
                          wordPrev == "goizeko"):
                        strHH = strNum
                        remainder = "am"
                        used = 0
                    elif (int(word) > 100 and
                          (
                        # wordPrev == "o" or
                        # wordPrev == "oh" or
                        wordPrev == "zero"
                    )):
                        # 0800 hours (pronounced oh-eight-hundred)
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        if wordNext == "orduak":
                            used += 1
                    elif (
                            wordNext == "orduak" and
                            word[0] != '0' and
                            (
                                int(word) < 100 and
                                int(word) > 2400
                            )):
                        # ignores military time
                        # "in 3 hours"
                        hrOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1

                    elif wordNext == "minutu":
                        # "in 10 minutes"
                        minOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext == "segundu":
                        # in 5 seconds
                        secOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif int(word) > 100:
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        if wordNext == "ordu":
                            used += 1

                    elif wordNext == "" or (
                            wordNext == "puntuan"):
                        strHH = word
                        strMM = 00
                        if wordNext == "puntuan":
                            used += 2
                            if wordNextNextNext == "arratsaldea":
                                remainder = "pm"
                                used += 1
                            elif wordNextNextNext == "goiza":
                                remainder = "am"
                                used += 1
                            elif wordNextNextNext == "gaua":
                                if 0 > strHH > 6:
                                    remainder = "am"
                                else:
                                    remainder = "pm"
                                used += 1

                    elif wordNext[0].isdigit():
                        strHH = word
                        strMM = wordNext
                        used += 1
                        if wordNextNext == "orduak":
                            used += 1
                    else:
                        isTime = False

            strHH = int(strHH) if strHH else 0
            strMM = int(strMM) if strMM else 0
            strHH = strHH + 12 if (remainder == "pm" and
                                   0 < strHH < 12) else strHH
            strHH = strHH - 12 if (remainder == "am" and
                                   0 < strHH >= 12) else strHH
            if strHH > 24 or strMM > 59:
                isTime = False
                used = 0
            if isTime:
                hrAbs = strHH * 1
                minAbs = strMM * 1
                used += 1

        if used > 0:
            # removed parsed words from the sentence
            for i in range(used):
                words[idx + i] = ""

            if wordPrev == "puntuan":
                words[words.index(wordPrev)] = ""

            if idx > 0 and wordPrev in time_indicators:
                words[idx - 1] = ""
            if idx > 1 and wordPrevPrev in time_indicators:
                words[idx - 2] = ""

            idx += used - 1
            found = True

    # check that we found a date
    if not date_found():
        return None

    if dayOffset is False:
        dayOffset = 0

    # perform date manipulation

    extractedDate = dateNow
    extractedDate = extractedDate.replace(microsecond=0,
                                          second=0,
                                          minute=0,
                                          hour=0)
    if datestr != "":
        en_months = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november',
                     'december']
        en_monthsShort = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july',
                          'aug',
                          'sept', 'oct', 'nov', 'dec']
        for idx, en_month in enumerate(en_months):
            datestr = datestr.replace(months[idx], en_month)
        for idx, en_month in enumerate(en_monthsShort):
            datestr = datestr.replace(monthsShort[idx], en_month)

        temp = datetime.strptime(datestr, "%B %d")
        temp = temp.replace(tzinfo=None)
        if not hasYear:
            temp = temp.replace(year=extractedDate.year, tzinfo=extractedDate.tzinfo)
            if extractedDate < temp:
                extractedDate = extractedDate.replace(year=int(currentYear),
                                                      month=int(
                                                          temp.strftime(
                                                              "%m")),
                                                      day=int(temp.strftime(
                                                          "%d")))
            else:
                extractedDate = extractedDate.replace(
                    year=int(currentYear) + 1,
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")))
        else:
            extractedDate = extractedDate.replace(
                year=int(temp.strftime("%Y")),
                month=int(temp.strftime("%m")),
                day=int(temp.strftime("%d")))

    if yearOffset != 0:
        extractedDate = extractedDate + relativedelta(years=yearOffset)
    if monthOffset != 0:
        extractedDate = extractedDate + relativedelta(months=monthOffset)
    if dayOffset != 0:
        extractedDate = extractedDate + relativedelta(days=dayOffset)

    if hrAbs is None and minAbs is None and default_time:
        hrAbs = default_time.hour
        minAbs = default_time.minute

    if hrAbs != -1 and minAbs != -1:
        extractedDate = extractedDate + relativedelta(hours=hrAbs or 0,
                                                      minutes=minAbs or 0)
        if (hrAbs or minAbs) and datestr == "":
            if not daySpecified and dateNow > extractedDate:
                extractedDate = extractedDate + relativedelta(days=1)
    if hrOffset != 0:
        extractedDate = extractedDate + relativedelta(hours=hrOffset)
    if minOffset != 0:
        extractedDate = extractedDate + relativedelta(minutes=minOffset)
    if secOffset != 0:
        extractedDate = extractedDate + relativedelta(seconds=secOffset)

    resultStr = " ".join(words)
    resultStr = ' '.join(resultStr.split())
    # resultStr = pt_pruning(resultStr)
    return [extractedDate, resultStr]


def get_gender_eu(word, raw_string=""):
    # There is no gender in Basque
    gender = False
    return gender
