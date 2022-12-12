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

# NOTE: This file as no use yet. It needs to be called from other functions

from collections import OrderedDict


# _ARTICLES_ES = {'el', 'la', 'los', 'las'}


_NUM_STRING_EU = {
    "zero": 0,
    "bat": 1,
    "bi": 2,
    "hiru": 3,
    "lau": 4,
    "bost": 5,
    "sei": 6,
    "zazpi": 7,
    "zortzi": 8,
    "bederatzi": 9,
    "hamar": 10,
    "hamaika": 11,
    "hamabi": 12,
    "hamahiru": 13,
    "hamalau": 14,
    "hamabost": 15,
    "hamasei": 16,
    "hamazazpi": 17,
    "hemezortzi": 18,
    "hemeretzi": 19,
    "hogei": 20,
    "hogeita hamar": 30,
    "hogeita hamaika": 31,
    "berrogei": 40,
    "berrogeita hamar": 50,
    "hirurogei": 60,
    "hirurogeita hamar": 70,
    "laurogei": 80,
    "laurogeita hamar": 90,
    "ehun": 100,
    "berrehun": 200,
    "hirurehun": 300,
    "laurehun": 400,
    "bostehun": 500,
    "seirehun": 600,
    "zazpirehun": 700,
    "zortzirehun": 800,
    "bederatzirehun": 900,
    "mila": 1000}


_FRACTION_STRING_EU = {
    2: 'erdia',
    3: 'herena',
    4: 'laurdena',
    5: 'bostena',
    6: 'seiena',
    7: 'zazpiena',
    8: 'zortziena',
    9: 'noveno',
    10: 'décimo',
    11: 'onceavo',
    12: 'doceavo',
    13: 'treceavo',
    14: 'catorceavo',
    15: 'quinceavo',
    16: 'dieciseisavo',
    17: 'diecisieteavo',
    18: 'dieciochoavo',
    19: 'diecinueveavo',
    20: 'veinteavo'
}

# https://www.grobauer.at/es_eur/zahlnamen.php
_LONG_SCALE_EU = OrderedDict([
    (100, 'ehuneko'),
    (1000, 'milaren'),
    (1000000, 'millón'),
    (1e9, "millardo"),
    (1e12, "billón"),
    (1e18, 'trillón'),
    (1e24, "cuatrillón"),
    (1e30, "quintillón"),
    (1e36, "sextillón"),
    (1e42, "septillón"),
    (1e48, "octillón"),
    (1e54, "nonillón"),
    (1e60, "decillón"),
    (1e66, "undecillón"),
    (1e72, "duodecillón"),
    (1e78, "tredecillón"),
    (1e84, "cuatrodecillón"),
    (1e90, "quindecillón"),
    (1e96, "sexdecillón"),
    (1e102, "septendecillón"),
    (1e108, "octodecillón"),
    (1e114, "novendecillón"),
    (1e120, "vigintillón"),
    (1e306, "unquinquagintillón"),
    (1e312, "duoquinquagintillón"),
    (1e336, "sexquinquagintillón"),
    (1e366, "unsexagintillón")
])


_SHORT_SCALE_EU = OrderedDict([
    (100, 'ehuneko'),
    (1000, 'milaren'),
    (1000000, 'millón'),
    (1e9, "billón"),
    (1e12, 'trillón'),
    (1e15, "cuatrillón"),
    (1e18, "quintillón"),
    (1e21, "sextillón"),
    (1e24, "septillón"),
    (1e27, "octillón"),
    (1e30, "nonillón"),
    (1e33, "decillón"),
    (1e36, "undecillón"),
    (1e39, "duodecillón"),
    (1e42, "tredecillón"),
    (1e45, "cuatrodecillón"),
    (1e48, "quindecillón"),
    (1e51, "sexdecillón"),
    (1e54, "septendecillón"),
    (1e57, "octodecillón"),
    (1e60, "novendecillón"),
    (1e63, "vigintillón"),
    (1e66, "unvigintillón"),
    (1e69, "uuovigintillón"),
    (1e72, "tresvigintillón"),
    (1e75, "quattuorvigintillón"),
    (1e78, "quinquavigintillón"),
    (1e81, "qesvigintillón"),
    (1e84, "septemvigintillón"),
    (1e87, "octovigintillón"),
    (1e90, "novemvigintillón"),
    (1e93, "trigintillón"),
    (1e96, "untrigintillón"),
    (1e99, "duotrigintillón"),
    (1e102, "trestrigintillón"),
    (1e105, "quattuortrigintillón"),
    (1e108, "quinquatrigintillón"),
    (1e111, "sestrigintillón"),
    (1e114, "septentrigintillón"),
    (1e117, "octotrigintillón"),
    (1e120, "noventrigintillón"),
    (1e123, "quadragintillón"),
    (1e153, "quinquagintillón"),
    (1e183, "sexagintillón"),
    (1e213, "septuagintillón"),
    (1e243, "octogintillón"),
    (1e273, "nonagintillón"),
    (1e303, "centillón"),
    (1e306, "uncentillón"),
    (1e309, "duocentillón"),
    (1e312, "trescentillón"),
    (1e333, "decicentillón"),
    (1e336, "undecicentillón"),
    (1e363, "viginticentillón"),
    (1e366, "unviginticentillón"),
    (1e393, "trigintacentillón"),
    (1e423, "quadragintacentillón"),
    (1e453, "quinquagintacentillón"),
    (1e483, "sexagintacentillón"),
    (1e513, "septuagintacentillón"),
    (1e543, "ctogintacentillón"),
    (1e573, "nonagintacentillón"),
    (1e603, "ducentillón"),
    (1e903, "trecentillón"),
    (1e1203, "quadringentillón"),
    (1e1503, "quingentillón"),
    (1e1803, "sexcentillón"),
    (1e2103, "septingentillón"),
    (1e2403, "octingentillón"),
    (1e2703, "nongentillón"),
    (1e3003, "millinillón")
])

# TODO: female forms.
_ORDINAL_STRING_BASE_EU = {
    1: 'lehenengo',
    2: 'bigarren',
    3: 'hirugarren',
    4: 'laugarren',
    5: 'bostgarren',
    6: 'seigarren',
    7: 'séptimo',
    8: 'octavo',
    9: 'noveno',
    10: 'décimo',
    11: 'undécimo',
    12: 'duodécimo',
    13: 'decimotercero',
    14: 'decimocuarto',
    15: 'decimoquinto',
    16: 'decimosexto',
    17: 'decimoséptimo',
    18: 'decimoctavo',
    19: 'decimonoveno',
    20: 'vigésimo',
    30: 'trigésimo',
    40: "cuadragésimo",
    50: "quincuagésimo",
    60: "sexagésimo",
    70: "septuagésimo",
    80: "octogésimo",
    90: "nonagésimo",
    10e3: "centésimó",
    1e3: "milésimo"
}


_SHORT_ORDINAL_STRING_EU = {
    1e6: "millonésimo",
    1e9: "milmillonésimo",
    1e12: "billonésimo",
    1e15: "milbillonésimo",
    1e18: "trillonésimo",
    1e21: "miltrillonésimo",
    1e24: "cuatrillonésimo",
    1e27: "milcuatrillonésimo",
    1e30: "quintillonésimo",
    1e33: "milquintillonésimo"
    # TODO > 1e-33
}
_SHORT_ORDINAL_STRING_EU.update(_ORDINAL_STRING_BASE_EU)


_LONG_ORDINAL_STRING_EU = {
    1e6: "millonésimo",
    1e12: "billionth",
    1e18: "trillonésimo",
    1e24: "cuatrillonésimo",
    1e30: "quintillonésimo",
    1e36: "sextillonésimo",
    1e42: "septillonésimo",
    1e48: "octillonésimo",
    1e54: "nonillonésimo",
    1e60: "decillonésimo"
    # TODO > 1e60
}
_LONG_ORDINAL_STRING_EU.update(_ORDINAL_STRING_BASE_EU)
