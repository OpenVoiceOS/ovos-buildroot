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
from collections import OrderedDict
from .parse_common import invert_dict

_FUNCTION_NOT_IMPLEMENTED_WARNING = "Tələb olunan funksiya Azərbaycan dilində yerinə yetirilmir."

_NUM_STRING_AZ = {
    0: 'sıfır',
    1: 'bir',
    2: 'iki',
    3: 'üç',
    4: 'dörd',
    5: 'beş',
    6: 'altı',
    7: 'yeddi',
    8: 'səkkiz',
    9: 'doqquz',
    10: 'on',
    11: 'on bir',
    12: 'on iki',
    13: 'on üç',
    14: 'on dörd',
    15: 'on beş',
    16: 'on altı',
    17: 'on yeddi',
    18: 'on səkkiz',
    19: 'on doqquz',
    20: 'iyirmi',
    30: 'otuz',
    40: 'qırx',
    50: 'əlli',
    60: 'altmış',
    70: 'yetmiş',
    80: 'səksən',
    90: 'doxsan'
}

_FRACTION_STRING_AZ = {
    2: 'ikidə',
    3: 'üçdə',
    4: 'dörddə',
    5: 'beşdə',
    6: 'altıda',
    7: 'yeddidə',
    8: 'səkkizdə',
    9: 'doqquzda',
    10: 'onda',
    11: 'on birdə',
    12: 'on ikidə',
    13: 'on üçdə',
    14: 'on dörddə',
    15: 'on beşdə',
    16: 'on altıda',
    17: 'on yeddidə',
    18: 'on səkkizdə',
    19: 'on doqquzda',
    20: 'iyirmidə',
    30: 'otuzda',
    40: 'qırxda',
    50: 'əllidə',
    60: 'altmışda',
    70: 'yetmişdə',
    80: 'səksəndə',
    90: 'doxsanda',
    1e2: 'yüzdə',
    1e3: 'mində'
}


_LONG_SCALE_AZ = OrderedDict([
    (100, 'yüz'),
    (1000, 'min'),
    (1000000, 'milyon'),
    (1e12, "milyard"),
    (1e18, 'trilyon'),
    (1e24, "kvadrilyon"),
    (1e30, "kvintilyon"),
    (1e36, "sekstilyon"),
    (1e42, "septilyon"),
    (1e48, "oktilyon"),
    (1e54, "nonilyon"),
    (1e60, "dekilyon")
])


_SHORT_SCALE_AZ = OrderedDict([
    (100, 'yüz'),
    (1000, 'min'),
    (1000000, 'milyon'),
    (1e9, "milyard"),
    (1e12, 'trilyon'),
    (1e15, "kvadrilyon"),
    (1e18, "kvintilyon"),
    (1e21, "sekstilyon"),
    (1e24, "septilyon"),
    (1e27, "oktilyon"),
    (1e30, "nonilyon"),
    (1e33, "dekilyon")
])

_ORDINAL_BASE_AZ = {
    1: 'birinci',
    2: 'ikinci',
    3: 'üçüncü',
    4: 'dördüncü',
    5: 'beşinci',
    6: 'altıncı',
    7: 'yeddinci',
    8: 'səkkizinci',
    9: 'doqquzuncu',
    10: 'onuncu',
    11: 'on birinci',
    12: 'on ikinci',
    13: 'on üçüncü',
    14: 'on dördüncü',
    15: 'on beşinci',
    16: 'on altıncı',
    17: 'on yeddinci',
    18: 'on səkkizinci',
    19: 'on doqquzuncu',
    20: 'iyirminci',
    30: 'otuzuncu',
    40: "qırxıncı",
    50: "əllinci",
    60: "altmışıncı",
    70: "yetmışinci",
    80: "səksəninci",
    90: "doxsanınçı",
    1e2: "yüzüncü",
    1e3: "mininci"
}

_SHORT_ORDINAL_AZ = {
    1e6: "milyonuncu",
    1e9: "milyardıncı",
    1e12: "trilyonuncu",
    1e15: "kvadrilyonuncu",
    1e18: "kvintilyonuncu",
    1e21: "sekstilyonuncu",
    1e24: "septilyonuncu",
    1e27: "oktilyonuncu",
    1e30: "nonilyonuncu",
    1e33: "dekilyonuncu"
    # TODO > 1e-33
}
_SHORT_ORDINAL_AZ.update(_ORDINAL_BASE_AZ)


_LONG_ORDINAL_AZ = {
    1e6: "milyonuncu",
    1e12: "milyardıncı",
    1e18: "trilyonuncu",
    1e24: "kvadrilyonuncu",
    1e30: "kvintilyonuncu",
    1e36: "sekstilyonuncu",
    1e42: "septilyonuncu",
    1e48: "oktilyonuncu",
    1e54: "nonilyonuncu",
    1e60: "dekilyonuncu"
    # TODO > 1e60
}
_LONG_ORDINAL_AZ.update(_ORDINAL_BASE_AZ)


# negate next number (-2 = 0 - 2)
_NEGATIVES_AZ = {"mənfi", "minus"}

# sum the next number (iyirmi iki = 20 + 2)
_SUMS_AZ = {'on', '10', 'iyirmi', '20', 'otuz', '30', 'qırx', '40', 'əlli', '50',
            'altmış', '60', 'yetmiş', '70', 'səksən', '80', 'doxsan', '90'}

_HARD_VOWELS = ['a', 'ı', 'o', 'u']
_SOFT_VOWELS = ['e', 'ə', 'i', 'ö', 'ü']
_VOWELS = _HARD_VOWELS + _SOFT_VOWELS

def _get_last_vowel(word):
    is_last = True
    for char in word[::-1]:
        if char in _VOWELS:
            return char, is_last
        is_last = False

    return "", is_last

def _last_vowel_type(word):
    return _get_last_vowel(word)[0] in _HARD_VOWELS

def _get_ordinal_ak(word):
    last_vowel, is_last = _get_last_vowel(word)
    if not last_vowel:
        return ""
    
    if last_vowel in ["a", "ı"]:
        if is_last:
            return "ncı"
        return "ıncı"

    if last_vowel == ["e", "ə", "i"]:
        if is_last:
            return "nci"
        return "inci"

    if last_vowel in ["o", "u"]:
        if is_last:
            return "ncu"
        return "uncu"

    if last_vowel == ["ö", "ü"]:
        if is_last:
            return "ncü"
        return "üncü"

def _get_full_time_ak(hour):
    if hour in [1, 3, 4, 5, 8, 11]:
        return "ə"
    if hour in [2, 7, 12]:
        return "yə"
    if hour in [9, 10]:
        return "a"
    return "ya"

def _get_half_time_ak(hour):
    if hour in [1, 5, 8, 11]:
        return "in"
    if hour in [2, 7, 12]:
        return "nin"
    if hour in [3, 4]:
        return "ün"
    if hour in [9, 10]:
        return "un"
    return "nın"

def _get_daytime(hour):
    if hour < 6:
        return "gecə"
    if hour < 12:
        return "səhər"
    if hour < 18:
        return "gündüz"
    return "axşam"

def _generate_plurals_az(originals):
    """
    Return a new set or dict containing the plural form of the original values,

    In Azerbaijani this means appending 'lar' or 'lər' to them according to the last vowel in word.

    Args:
        originals set(str) or dict(str, any): values to pluralize

    Returns:
        set(str) or dict(str, any)

    """
    
    if isinstance(originals, dict):
        return {key + ('lar' if _last_vowel_type(key) else 'lər'): value for key, value in originals.items()}
    return {value + ('lar' if _last_vowel_type(value) else 'lər') for value in originals}


_MULTIPLIES_LONG_SCALE_AZ = set(_LONG_SCALE_AZ.values()) | \
    set(_LONG_SCALE_AZ.values())

_MULTIPLIES_SHORT_SCALE_AZ = set(_SHORT_SCALE_AZ.values()) | \
    set(_SHORT_SCALE_AZ.values())

# split sentence parse separately and sum ( 2 and a half = 2 + 0.5 )
_FRACTION_MARKER_AZ = {"və"}

# decimal marker ( 1 nöqtə 5 = 1 + 0.5)
_DECIMAL_MARKER_AZ = {"nöqtə"}

_STRING_NUM_AZ = invert_dict(_NUM_STRING_AZ)

_SPOKEN_EXTRA_NUM_AZ = {
            "yarım": 0.5,
            "üçdəbir": 1 / 3,
            "dörddəbir": 1 / 4
        }

_STRING_SHORT_ORDINAL_AZ = invert_dict(_SHORT_ORDINAL_AZ)
_STRING_LONG_ORDINAL_AZ = invert_dict(_LONG_ORDINAL_AZ)
