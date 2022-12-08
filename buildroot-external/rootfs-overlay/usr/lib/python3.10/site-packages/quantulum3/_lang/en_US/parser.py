#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

import logging
import re

from ... import classes as cls
from ... import load, parser
from ... import regex as reg
from . import lang
from .load import COMMON_WORDS

_LOGGER = logging.getLogger(__name__)


###############################################################################
def clean_surface(surface, span):
    """
    Remove spurious characters from a quantity's surface.
    """

    surface = surface.replace("-", " ")
    no_start = ["and", " "]
    no_end = [" "] + [" {}".format(misc) for misc in reg.miscnum(lang)]

    found = True
    while found:
        found = False
        for word in no_start:
            if surface.lower().startswith(word):
                surface = surface[len(word) :]
                span = (span[0] + len(word), span[1])
                found = True
        for word in no_end:
            if surface.lower().endswith(word):
                surface = surface[: -len(word)]
                span = (span[0], span[1] - len(word))
                found = True

    if not surface:
        return None, None

    split = surface.lower().split()
    if (
        split[0] in reg.miscnum(lang)
        and len(split) > 1
        and split[1] in reg.units(lang) + reg.tens(lang)
    ):
        span = (span[0] + len(surface.split()[0]) + 1, span[1])
        surface = " ".join(surface.split()[1:])

    return surface, span


###############################################################################
def extract_spellout_values(text):
    """
    Convert spelled out numbers in a given text to digits.
    """

    values = []
    for item in reg.text_pattern_reg(lang).finditer(text):
        try:
            surface, span = clean_surface(item.group(0), item.span())
            if not surface or surface.lower() in reg.scales(lang):
                continue
            curr = result = 0.0
            for word in surface.lower().split():
                try:
                    scale, increment = (
                        1,
                        float(
                            re.sub(
                                r"(-$|[%s])" % reg.grouping_operators_regex(lang),
                                "",
                                word,
                            )
                        ),
                    )
                except ValueError:
                    match = re.search(reg.numberwords_regex(), word)
                    scale, increment = reg.numberwords(lang)[match.group(0)]
                curr = curr * scale + increment
                if scale > 100:
                    result += curr
                    curr = 0.0
            values.append(
                {
                    "old_surface": surface,
                    "old_span": span,
                    "new_surface": str(result + curr),
                }
            )
        except (KeyError, AttributeError):
            # just ignore the match if an error occurred
            pass

    return sorted(values, key=lambda x: x["old_span"][0])


###############################################################################
def parse_unit(_, unit, slash):
    """
    Parse surface and power from unit text.
    """

    surface = unit.replace(".", "")
    power = re.findall(r"-?[0-9%s]+" % reg.unicode_superscript_regex(), surface)
    power_written = re.findall(r"\b(%s)\b" % "|".join(reg.powers(lang)), surface)

    if power:
        power = [
            reg.unicode_superscript()[i] if i in reg.unicode_superscript() else i
            for i in power
        ]
        power = "".join(power)
        new_power = -1 * int(power) if slash else int(power)
        surface = re.sub(r"\^?-?[0-9%s]+" % reg.unicode_superscript(), "", surface)

    elif power_written:
        exponent = reg.powers(lang)[power_written[0]]
        new_power = -exponent if slash else exponent
        surface = re.sub(r"\b%s\b" % power_written[0], "", surface).strip()

    else:
        new_power = -1 if slash else 1

    return surface, new_power


###############################################################################
def build_quantity(orig_text, text, item, values, unit, surface, span, uncert):
    """
    Build a Quantity object out of extracted information.
    """
    # TODO rerun if change occurred
    # Re parse unit if a change occurred
    dimension_change = True

    # Extract "absolute " ...
    _absolute = "absolute "
    if (
        unit.name == "dimensionless"
        and _absolute == orig_text[span[0] - len(_absolute) : span[0]]
    ):
        unit = load.units(lang).names["kelvin"]
        unit.original_dimensions = unit.dimensions
        surface = _absolute + surface
        span = (span[0] - len(_absolute), span[1])
        dimension_change = True

    # Usually "$3T" does not stand for "dollar tesla"
    # this holds as well for "3k miles"
    # TODO use classifier to decide if 3K is 3 thousand or 3 Kelvin
    if unit.entity.dimensions:
        if (
            len(unit.entity.dimensions) > 1
            and unit.entity.dimensions[0]["base"] == "currency"
            and unit.original_dimensions[1]["surface"] in reg.suffixes(lang).keys()
        ):
            suffix = unit.original_dimensions[1]["surface"]
            # Only apply if at least last value is suffixed by k, M, etc
            if re.search(r"\d{}\b".format(suffix), text):
                values = [value * reg.suffixes(lang)[suffix] for value in values]
                unit.original_dimensions = [
                    unit.original_dimensions[0]
                ] + unit.original_dimensions[2:]
                dimension_change = True

        elif unit.original_dimensions[0]["surface"] in reg.suffixes(lang).keys():
            # k/M etc is only applied if non-symbolic surfaces of other units
            # (because colloquial) or currency units
            symbolic = all(
                dim["surface"] in load.units(lang).names[dim["base"]].symbols
                for dim in unit.original_dimensions[1:]
            )
            if not symbolic:
                suffix = unit.original_dimensions[0]["surface"]
                values = [value * reg.suffixes(lang)[suffix] for value in values]
                unit.original_dimensions = unit.original_dimensions[1:]
                dimension_change = True

    # Usually "1990s" stands for the decade, not the amount of seconds
    elif re.match(r"[1-2]\d\d0s", surface):
        unit.original_dimensions = []
        dimension_change = True
        surface = surface[:-1]
        span = (span[0], span[1] - 1)
        _LOGGER.debug('\tCorrect for "1990s" pattern')

    # Usually "1am", "5.12 pm" stand for the time, not pico- or attometer
    if (
        len(unit.dimensions) == 1
        and ("pm" == item.group("unit1") or "am" == item.group("unit1"))
        and unit.entity.name == "length"
        and re.fullmatch(r"\d(\.\d\d)?", item.group("value"))
    ):
        _LOGGER.debug("\tCorrect for am/pm time pattern")
        return

    # When it comes to currencies, some users prefer the format ($99.99) instead of -$99.99
    try:
        if (
            len(values) == 1
            and unit.entity.name == "currency"
            and span[0] > 0
            and orig_text[span[0] - 1] == "("
            and orig_text[span[1]] == ")"
            and values[0] >= 0
        ):
            span = (span[0] - 1, span[1] + 1)
            surface = "({})".format(surface)
            values[0] = -values[0]
    except IndexError:
        pass

    # check if a unit without operators, actually is a common word
    pruned_common_word = unit.original_dimensions
    while pruned_common_word:
        pruned_common_word = False

        # TODO quick hack that works, do remove and eventually merge with common word removal
        # Usually "in" stands for the preposition, not inches
        if (
            unit.original_dimensions
            and unit.original_dimensions[-1]["base"] == "inch"
            and re.search(r" in$", surface)
            and "/" not in surface
            and not re.search(
                r" in(\.|,|\?|!|$)",
                orig_text[span[0] : min(len(orig_text), span[1] + 1)],
            )
        ):
            unit.original_dimensions = unit.original_dimensions[:-1]
            dimension_change = True
            pruned_common_word = True
            surface = surface[:-3]
            span = (span[0], span[1] - 3)
            _LOGGER.debug("\tCorrect for 'in' pattern")
            continue

        # Usually "my" stands for the determiner, not megayear
        if (
            unit.original_dimensions
            and unit.original_dimensions[-1]["base"] == "megayear"
            and re.search(r" my$", surface)
            and "/" not in surface
            and not re.search(
                r" my(\.|,|\?|!|$)",
                orig_text[span[0] : min(len(orig_text), span[1] + 1)],
            )
        ):
            unit.original_dimensions = unit.original_dimensions[:-1]
            dimension_change = True
            pruned_common_word = True
            surface = surface[:-3]
            span = (span[0], span[1] - 3)
            _LOGGER.debug("\tCorrect for 'my' pattern")
            continue

        candidates = [u["power"] == 1 for u in unit.original_dimensions]
        for start in range(0, len(unit.original_dimensions)):
            for end in reversed(range(start + 2, len(unit.original_dimensions) + 1)):
                # Try to match a combination of >1 consecutive surfaces with a
                # common 4 letter word
                if not all(candidates[start:end]):
                    continue
                combination = "".join(
                    u.get("surface", "") for u in unit.original_dimensions[start:end]
                )
                # Combination has to be at least one letter
                if len(combination) < 1:
                    continue
                # Combination may have any capitalization due to possible common names
                # i.e. PayPal, iPhone, LaTeX
                # Combination has to be inside the surface
                if combination not in surface:
                    continue
                # Combination has to be a common word
                if combination.lower() not in COMMON_WORDS[len(combination)]:
                    continue
                # Cut the combination from the surface and everything that
                # follows as it is a word, it will be preceded by a space
                match = re.search(r"[-\s]%s\b" % combination, surface)
                if not match:
                    continue
                span = (span[0], span[0] + match.start())
                surface = surface[: match.start()]
                unit.original_dimensions = unit.original_dimensions[:start]
                dimension_change = True
                pruned_common_word = True
                _LOGGER.debug(
                    "\tDetected common word '{}' and removed it".format(combination)
                )
                continue

    match = parser.is_quote_artifact(text, item.span())
    if match:
        surface = surface[:-1]
        span = (span[0], span[1] - 1)
        if unit.original_dimensions and (
            unit.original_dimensions[-1]["surface"] == '"'
        ):
            unit.original_dimensions = unit.original_dimensions[:-1]
            dimension_change = True
        _LOGGER.debug("\tCorrect for quotes")

    if (
        re.search(r" time$", surface)
        and unit.original_dimensions
        and len(unit.original_dimensions) > 1
        and unit.original_dimensions[-1]["base"] == "count"
    ):
        unit.original_dimensions = unit.original_dimensions[:-1]
        dimension_change = True
        surface = surface[:-5]
        span = (span[0], span[1] - 5)
        _LOGGER.debug('\tCorrect for "time"')

    if dimension_change:
        if unit.original_dimensions:
            unit = parser.get_unit_from_dimensions(
                unit.original_dimensions, orig_text, lang
            )
        else:
            unit = load.units(lang).names["dimensionless"]

    # Discard irrelevant txt2float extractions, cardinal numbers, codes etc.
    if (
        surface.lower() in ["a", "an", "one"]
        or re.search(r"1st|2nd|3rd|[04-9]th", surface)
        or re.search(r"\d+[A-Z]+\d+", surface)
        or re.search(r"\ba second\b", surface, re.IGNORECASE)
    ):
        _LOGGER.debug('\tMeaningless quantity ("%s"), discard', surface)
        return

    objs = []
    for value in values:
        obj = cls.Quantity(
            value=value,
            unit=unit,
            surface=surface,
            span=span,
            uncertainty=uncert,
            lang=lang,
        )
        objs.append(obj)

    return objs


###############################################################################
def clean_text(text):
    """
    Clean text before parsing, language specific part
    """

    # Replace genitives
    text = re.sub(r"(?<=\w)(\'s\b|s\')(?!\w)", "  ", text)

    return text


###############################################################################
def name_from_dimensions(dimensions):
    """
    Build the name of a unit from its dimensions.
    Param:
        dimensions: List of dimensions
    """

    name = ""

    for unit in dimensions:
        if unit["power"] < 0:
            name += "per "
        power = abs(unit["power"])
        if power == 1:
            name += unit["base"]
        elif power == 2:
            name += "square " + unit["base"]
        elif power == 3:
            name += "cubic " + unit["base"]
        elif power > 3:
            name += unit["base"] + " to the %g" % power
        name += " "

    name = name.strip()

    return name
