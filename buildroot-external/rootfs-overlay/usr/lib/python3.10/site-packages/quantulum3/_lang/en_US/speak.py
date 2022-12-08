#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` class to spoken conversion.
"""

from ... import load, parser
from . import lang


###############################################################################
def quantity_to_spoken(quantity):
    """
    Express quantity as a speakable string
    :return: Speakable version of this quantity
    """
    count = quantity.value
    unit_string = quantity.unit.to_spoken(count)
    return "{}{}{}".format(
        load.number_to_words(count), " " if len(unit_string) else "", unit_string
    )


###############################################################################
def unit_to_spoken(unit, count=1):
    """
    Convert a given unit to the unit in words, correctly inflected.
    :param unit: The unit to be converted
    :param count: The value of the quantity (i.e. 1 for one watt, 2 for two
                  seconds)
    :return: A string with the correctly inflected spoken version of the unit
    """
    if unit.surfaces:
        unit_string = unit.surfaces[0]
        unit_string = load.pluralize(unit_string, count)
    else:
        # derived unit
        denominator_dimensions = [i for i in unit.dimensions if i["power"] > 0]
        denominator_string = parser.name_from_dimensions(denominator_dimensions, lang)
        plural_denominator_string = load.pluralize(denominator_string)
        unit_string = unit.name.replace(denominator_string, plural_denominator_string)
    return unit_string
