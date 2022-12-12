#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` unit and entity loading functions.
"""

import json
import os
from builtins import open
from collections import defaultdict

import inflect

from ... import load
from . import lang

TOPDIR = os.path.dirname(__file__) or "."

PLURALS = inflect.engine()


###############################################################################
def pluralize(singular, count=None):
    return PLURALS.plural(singular, count)


def number_to_words(number):
    return PLURALS.number_to_words(number)


###############################################################################
def build_common_words():
    # Read raw 4 letter file
    path = os.path.join(TOPDIR, "common-units.txt")
    with open(path, "r", encoding="utf-8") as file:
        common_units = {line.strip() for line in file if not line.startswith("#")}
    path = os.path.join(TOPDIR, "common-words.txt")
    words = defaultdict(list)  # Collect words based on length
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                continue
            line = line.rstrip()
            if (
                line not in load.units(lang).surfaces_lower
                and line not in load.units(lang).symbols
                and line not in common_units
            ):
                words[len(line)].append(line)
            plural = load.pluralize(line)
            if (
                plural not in load.units(lang).surfaces_all
                and plural not in load.units(lang).symbols
                and plural not in common_units
            ):
                words[len(plural)].append(plural)
    return words


###############################################################################
def load_common_words():
    path = os.path.join(TOPDIR, "common-words.json")
    dumped = {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            dumped = json.load(file)
    except OSError:  # pragma: no cover
        pass

    words = defaultdict(list)  # Collect words based on length
    for length, word_list in dumped.items():
        words[int(length)] = word_list
    return words


COMMON_WORDS = load_common_words()
