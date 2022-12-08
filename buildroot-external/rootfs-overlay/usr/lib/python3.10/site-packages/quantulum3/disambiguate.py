# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions.
"""

from . import classifier as clf
from . import load
from . import no_classifier as no_clf


###############################################################################
def disambiguate_unit(unit_surface, text, lang="en_US"):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    :returns (str) unit name of the resolved unit
    """
    if clf.USE_CLF:
        base = clf.disambiguate_unit(unit_surface, text, lang).name
    else:
        base = (
            load.units(lang).symbols[unit_surface]
            or load.units(lang).surfaces[unit_surface]
            or load.units(lang).surfaces_lower[unit_surface.lower()]
            or load.units(lang).symbols_lower[unit_surface.lower()]
        )

        if len(base) > 1:
            base = no_clf.disambiguate_no_classifier(base, text, lang)
        elif len(base) == 1:
            base = next(iter(base))

        if base:
            base = base.name
        else:
            base = "unk"

    return base


###############################################################################
def disambiguate_entity(key, text, lang="en_US"):
    """
    Resolve ambiguity between entities with same dimensionality.
    """
    try:
        if clf.USE_CLF:
            ent = clf.disambiguate_entity(key, text, lang)
        else:
            derived = load.entities().derived[key]
            if len(derived) > 1:
                ent = no_clf.disambiguate_no_classifier(derived, text, lang)
                ent = load.entities().names[ent]
            elif len(derived) == 1:
                ent = next(iter(derived))
            else:
                ent = None
    except (KeyError, StopIteration):
        ent = None

    return ent
