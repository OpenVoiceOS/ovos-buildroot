#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` regex functions.
"""

import re

from . import language, load
from .load import cached


###############################################################################
@cached
def _get_regex(lang="en_US"):
    """
    Get regex module for given language
    :param lang:
    :return:
    """
    return language.get("regex", lang)


###############################################################################
def units(lang="en_US"):
    return _get_regex(lang).UNITS


def tens(lang="en_US"):
    return _get_regex(lang).TENS


def scales(lang="en_US"):
    return _get_regex(lang).SCALES


def decimals(lang="en_US"):
    return _get_regex(lang).DECIMALS


def miscnum(lang="en_US"):
    return _get_regex(lang).MISCNUM


def powers(lang="en_US"):
    return _get_regex(lang).POWERS


def exponents_regex(lang="en_US"):
    return _get_regex(lang).EXPONENTS_REGEX


@cached
def ranges(lang="en_US"):
    ranges_ = {"-"}
    ranges_.update(_get_regex(lang).RANGES)
    return ranges_


@cached
def uncertainties(lang="en_US"):
    uncertainties_ = {r"\+/-", r"±"}
    uncertainties_.update(_get_regex(lang).UNCERTAINTIES)
    return uncertainties_


###############################################################################
@cached
def numberwords(lang="en_US"):
    """
    Convert number words to integers in a given text.
    """

    numwords = {}

    numwords.update(miscnum(lang))

    for idx, word in enumerate(units(lang)):
        numwords[word] = (1, idx)
    for idx, word in enumerate(tens(lang)):
        numwords[word] = (1, idx * 10)
    for idx, word in enumerate(scales(lang)):
        numwords[word] = (10 ** (idx * 3 or 2), 0)
    for word, factor in decimals(lang).items():
        numwords[word] = (factor, 0)
        numwords[load.pluralize(word, lang=lang)] = (factor, 0)

    return numwords


@cached
def numberwords_regex(lang="en_US"):
    all_numbers = r"|".join(
        r"((?<=\W)|^)%s((?=\W)|$)" % i for i in list(numberwords(lang).keys()) if i
    )
    return all_numbers


###############################################################################
def suffixes(lang="en_US"):
    return _get_regex(lang).SUFFIXES


def unicode_superscript():
    uni_super = {
        u"¹": "1",
        u"²": "2",
        u"³": "3",
        u"⁴": "4",
        u"⁵": "5",
        u"⁶": "6",
        u"⁷": "7",
        u"⁸": "8",
        u"⁹": "9",
        u"⁰": "0",
    }
    return uni_super


def unicode_superscript_regex():
    return re.escape("".join(list(unicode_superscript().keys())))


def unicode_fractions():
    uni_frac = {
        u"¼": "1/4",
        u"½": "1/2",
        u"¾": "3/4",
        u"⅐": "1/7",
        u"⅑": "1/9",
        u"⅒": "1/10",
        u"⅓": "1/3",
        u"⅔": "2/3",
        u"⅕": "1/5",
        u"⅖": "2/5",
        u"⅗": "3/5",
        u"⅘": "4/5",
        u"⅙": "1/6",
        u"⅚": "5/6",
        u"⅛": "1/8",
        u"⅜": "3/8",
        u"⅝": "5/8",
        u"⅞": "7/8",
    }
    return uni_frac


def unicode_fractions_regex():
    return re.escape("".join(list(unicode_fractions().keys())))


@cached
def multiplication_operators(lang="en_US"):
    mul = {u"*", u" ", u"·", u"x"}
    mul.update(_get_regex(lang).MULTIPLICATION_OPERATORS)
    return mul


@cached
def multiplication_operators_regex(lang="en_US"):
    return r"|".join(r"%s" % re.escape(i) for i in multiplication_operators(lang))


@cached
def division_operators(lang="en_US"):
    div = {u"/"}
    div.update(_get_regex(lang).DIVISION_OPERATORS)
    return div


@cached
def grouping_operators(lang="en_US"):
    grouping_ops = {" "}
    grouping_ops.update(_get_regex(lang).GROUPING_OPERATORS)
    return grouping_ops


def grouping_operators_regex(lang="en_US"):
    return "".join(grouping_operators(lang))


@cached
def decimal_operators(lang="en_US"):
    return _get_regex(lang).DECIMAL_OPERATORS


@cached
def decimal_operators_regex(lang="en_US"):
    return "".join(decimal_operators(lang))


@cached
def operators(lang="en_US"):
    ops = set()
    ops.update(multiplication_operators(lang))
    ops.update(division_operators(lang))
    return ops


# Pattern for extracting a digit-based number
NUM_PATTERN = r"""
    (?{number}              # required number
        [+-]?                  #   optional sign
        (\.?\d+|[{unicode_fract}])     #   required digits or unicode fraction
        (?:[{grouping}]\d{{3}})*         #   allowed grouping
        (?{decimals}[{decimal_operators}]\d+)?    #   optional decimals
    )
    (?{scale}               # optional exponent
        (?:{multipliers})?                #   multiplicative operators
        (?{base}(E|e|\d+)\^?)    #   required exponent prefix
        (?{exponent}[+-]?\d+|[{superscript}]) # required exponent, superscript
                                              # or normal
    )?
    (?{fraction}             # optional fraction
        \ \d+/\d+|\ ?[{unicode_fract}]|/\d+
    )?

"""


# Pattern for extracting a digit-based number
def number_pattern():
    return NUM_PATTERN


@cached
def number_pattern_no_groups(lang="en_US"):
    return NUM_PATTERN.format(
        number=":",
        decimals=":",
        scale=":",
        base=":",
        exponent=":",
        fraction=":",
        grouping=grouping_operators_regex(lang),
        multipliers=multiplication_operators_regex(lang),
        superscript=unicode_superscript_regex(),
        unicode_fract=unicode_fractions_regex(),
        decimal_operators=decimal_operators_regex(lang),
    )


@cached
def number_pattern_groups(lang="en_US"):
    return NUM_PATTERN.format(
        number="P<number>",
        decimals="P<decimals>",
        scale="P<scale>",
        base="P<base>",
        exponent="P<exponent>",
        fraction="P<fraction>",
        grouping=grouping_operators_regex(lang),
        multipliers=multiplication_operators_regex(lang),
        superscript=unicode_superscript_regex(),
        unicode_fract=unicode_fractions_regex(),
        decimal_operators=decimal_operators_regex(lang),
    )


@cached
def range_pattern(lang="en_US"):
    num_pattern_no_groups = number_pattern_no_groups(lang)
    return r"""                        # Pattern for a range of numbers

    (?:                                    # First number
        (?<![a-zA-Z0-9+.-])                # lookbehind, avoid "Area51"
        %s
    )
    (?:                                    # Second number
        \ ?(?:(?:-\ )?(?:%s|%s))\ ?  # Group for ranges or uncertainties
    %s)?

    """ % (
        num_pattern_no_groups,
        "|".join(ranges(lang)),
        "|".join(uncertainties(lang)),
        num_pattern_no_groups,
    )


@cached
def text_pattern_reg(lang="en_US"):
    txt_pattern = _get_regex(lang).TEXT_PATTERN.format(
        number_pattern_no_groups=number_pattern_no_groups(lang),
        numberwords_regex=numberwords_regex(lang),
    )
    reg_txt = re.compile(txt_pattern, re.VERBOSE | re.IGNORECASE)
    return reg_txt


###############################################################################
@cached
def units_regex(lang="en_US"):
    """
    Build a compiled regex object. Groups of the extracted items, with 4
    repetitions, are:

        0: whole surface
        1: prefixed symbol
        2: numerical value
        3: first operator
        4: first unit
        5: second operator
        6: second unit
        7: third operator
        8: third unit
        9: fourth operator
        10: fourth unit

    Example, 'I want $20/h'

        0: $20/h
        1: $
        2: 20
        3: /
        4: h
        5: None
        6: None
        7: None
        8: None
        9: None
        10: None

    """

    op_keys = sorted(list(operators(lang)), key=len, reverse=True)
    unit_keys = sorted(
        list(load.units(lang).surfaces.keys()) + list(load.units(lang).symbols.keys()),
        key=len,
        reverse=True,
    )
    symbol_keys = sorted(
        list(load.units(lang).prefix_symbols.keys()), key=len, reverse=True
    )

    exponent = exponents_regex(lang).format(superscripts=unicode_superscript_regex())

    all_ops = "|".join([r"{}".format(re.escape(i)) for i in op_keys])
    all_units = "|".join([r"{}".format(re.escape(i)) for i in unit_keys])
    all_symbols = "|".join([r"{}".format(re.escape(i)) for i in symbol_keys])

    pattern = r"""
        (?<!\w)                                     # "begin" of word
        (?P<prefix>(?:%s)(?![a-zA-Z]))?         # Currencies, mainly
        (?P<value>%s)-?                           # Number
        (?:(?P<operator1>%s(?=(%s)%s))?(?P<unit1>(?:%s)%s)?)    # Operator + Unit (1)
        (?:(?P<operator2>%s(?=(%s)%s))?(?P<unit2>(?:%s)%s)?)    # Operator + Unit (2)
        (?:(?P<operator3>%s(?=(%s)%s))?(?P<unit3>(?:%s)%s)?)    # Operator + Unit (3)
        (?:(?P<operator4>%s(?=(%s)%s))?(?P<unit4>(?:%s)%s)?)    # Operator + Unit (4)
        (?!\w)                                      # "end" of word
    """ % tuple(
        [all_symbols, range_pattern(lang)]
        + 4 * [all_ops, all_units, exponent, all_units, exponent]
    )
    regex = re.compile(pattern, re.VERBOSE | re.IGNORECASE)

    return regex
