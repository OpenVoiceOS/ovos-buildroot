#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classes.
"""

import num2words

from . import language


###############################################################################
def _get_speak(lang):
    return language.get("speak", lang)


###############################################################################
def quantity_to_spoken(quantity, lang):
    """
    Express quantity as a speakable string
    :return: Speakable version of this quantity
    """
    count = quantity.value
    if quantity.unit.entity.name == "currency" and quantity.unit.currency_code:
        try:
            return num2words.num2words(
                count, lang=lang, to="currency", currency=quantity.unit.currency_code
            )
        except NotImplementedError:
            pass
    return _get_speak(lang).quantity_to_spoken(quantity)


###############################################################################
def unit_to_spoken(unit, count, lang):
    if unit.name == "dimensionless":
        return ""
    else:
        return _get_speak(lang).unit_to_spoken(unit, count)
