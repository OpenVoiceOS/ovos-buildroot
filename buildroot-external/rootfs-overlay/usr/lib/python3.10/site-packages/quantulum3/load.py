#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` unit and entity loading functions.
"""

import json
from collections import defaultdict
from pathlib import Path

from . import classes as c
from . import language

TOPDIR = Path(__file__).parent or Path(".")

###############################################################################
_CACHE_DICT = {}


def cached(funct):
    """
    Decorator for caching language specific data
    :param funct: the method, dynamically responding to language. Only
                  parameter is lang
    :return: the method, dynamically responding to language but also caching
             results
    """
    assert callable(funct)

    def cached_function(lang="en_US"):
        try:
            return _CACHE_DICT[id(funct)][lang]
        except KeyError:
            result = funct(lang)
            _CACHE_DICT[id(funct)] = {lang: result}
            return result

    return cached_function


###############################################################################
@cached
def _get_load(lang="en_US"):
    return language.get("load", lang)


###############################################################################
def to_int_iff_int(value):
    """
    Returns int type number if the value is an integer value
    :param value:
    :return:
    """
    try:
        if int(value) == value:
            return int(value)
    except (TypeError, ValueError):
        pass
    return value


def pluralize(singular, count=None, lang="en_US"):
    # Make spelling integers more natural
    count = to_int_iff_int(count)
    return _get_load(lang).pluralize(singular, count)


def number_to_words(count, lang="en_US"):
    # Make spelling integers more natural
    count = to_int_iff_int(count)
    return _get_load(lang).number_to_words(count)


###############################################################################
METRIC_PREFIXES = {
    "Y": "yotta",
    "Z": "zetta",
    "E": "exa",
    "P": "peta",
    "T": "tera",
    "G": "giga",
    "M": "mega",
    "k": "kilo",
    "h": "hecto",
    "da": "deca",
    "d": "deci",
    "c": "centi",
    "m": "milli",
    "µ": "micro",
    "n": "nano",
    "p": "pico",
    "f": "femto",
    "a": "atto",
    "z": "zepto",
    "y": "yocto",
    "Ki": "kibi",
    "Mi": "mebi",
    "Gi": "gibi",
    "Ti": "tebi",
    "Pi": "pebi",
    "Ei": "exbi",
    "Zi": "zebi",
    "Yi": "yobi",
}


###############################################################################
def get_key_from_dimensions(derived):
    """
    Translate dimensionality into key for DERIVED_UNI and DERIVED_ENT dicts.
    """

    return tuple((i["base"], i["power"]) for i in derived)


###############################################################################
class Entities(object):
    def __init__(self, lang="en_US"):
        """
        Load entities from JSON file.
        """

        path = TOPDIR.joinpath("entities.json")
        with path.open(encoding="utf-8") as file:
            general_entities = json.load(file)
        names = [i["name"] for i in general_entities]

        try:
            assert len(set(names)) == len(general_entities)
        except AssertionError:  # pragma: no cover
            raise Exception(
                "Entities with same name: %s" % [i for i in names if names.count(i) > 1]
            )

        self.names = dict(
            (
                k["name"],
                c.Entity(name=k["name"], dimensions=k["dimensions"], uri=k["URI"]),
            )
            for k in general_entities
        )

        # Update with language specific URI
        with TOPDIR.joinpath(language.topdir(lang), "entities.json").open(
            "r", encoding="utf-8"
        ) as file:
            lang_entities = json.load(file)
        for ent in lang_entities:
            general_entities[ent["name"]].uri = ent["URI"]

        # Generate derived units
        derived_ent = defaultdict(set)
        for entity in self.names.values():
            if not entity.dimensions:
                continue
            perms = self.get_dimension_permutations(entity.dimensions)
            for perm in perms:
                key = get_key_from_dimensions(perm)
                derived_ent[key].add(entity)

        self.derived = derived_ent

    def get_dimension_permutations(self, derived):
        """
        Get all possible dimensional definitions for an entity.
        """

        new_derived = defaultdict(int)
        for item in derived:
            new = self.names[item["base"]].dimensions
            if new:
                for new_item in new:
                    new_derived[new_item["base"]] += new_item["power"] * item["power"]
            else:
                new_derived[item["base"]] += item["power"]

        final = [
            [{"base": i[0], "power": i[1]} for i in list(new_derived.items())],
            derived,
        ]
        final = [sorted(i, key=lambda x: x["base"]) for i in final]

        candidates = []
        for item in final:
            if item not in candidates:
                candidates.append(item)

        return candidates


@cached
def entities(lang="en_US"):
    """
    Cached entity object
    """
    return Entities(lang)


###############################################################################
def get_derived_units(names):
    """
    Create dictionary of unit dimensions.
    """

    derived_uni = {}

    for name in names:
        key = get_key_from_dimensions(names[name].dimensions)
        derived_uni[key] = names[name]
        plain_derived = [{"base": name, "power": 1}]
        key = get_key_from_dimensions(plain_derived)
        derived_uni[key] = names[name]
        if not names[name].dimensions:
            names[name].dimensions = plain_derived
        names[name].dimensions = [
            {"base": names[i["base"]].name, "power": i["power"]}
            for i in names[name].dimensions
        ]

    return derived_uni


###############################################################################
class Units(object):
    def __init__(self, lang="en_US"):
        """
        Load units from JSON file.
        """
        self.lang = lang

        # names of all units
        self.names = {}
        self.symbols, self.symbols_lower = defaultdict(set), defaultdict(set)
        self.surfaces, self.surfaces_lower = defaultdict(set), defaultdict(set)
        self.prefix_symbols = defaultdict(set)

        # Load general units
        path = TOPDIR.joinpath("units.json")
        with path.open(encoding="utf-8") as file:
            general_units = json.load(file)
        # load language specifics
        path = TOPDIR.joinpath(language.topdir(lang), "units.json")
        with path.open(encoding="utf-8") as file:
            lang_units = json.load(file)

        unit_dict = {}
        for unit in general_units.copy():
            general_units.extend(self.prefixed_units(unit))
        for unit in general_units:
            unit_dict[unit["name"]] = unit
        for unit in lang_units.copy():
            lang_units.extend(self.prefixed_units(unit))
        for unit in lang_units:
            unit_dict[unit["name"]] = unit_dict.get(unit["name"], unit)
            unit_dict[unit["name"]].update(unit)

        for unit in unit_dict.values():
            self.load_unit(unit)

        self.derived = get_derived_units(self.names)

        # symbols of all units
        self.symbols_all = self.symbols.copy()
        self.symbols_all.update(self.symbols_lower)

        # surfaces of all units
        self.surfaces_all = self.surfaces.copy()
        self.surfaces_all.update(self.surfaces_lower)

    def load_unit(self, unit):
        try:
            assert unit["name"] not in self.names
        except AssertionError:  # pragma: no cover
            msg = "Two units with same name in units.json: %s" % unit["name"]
            raise Exception(msg)

        obj = c.Unit(
            name=unit["name"],
            surfaces=unit.get("surfaces", []),
            entity=entities().names[unit["entity"]],
            uri=unit["URI"],
            symbols=unit.get("symbols", []),
            dimensions=unit.get("dimensions", []),
            currency_code=unit.get("currency_code"),
            lang=self.lang,
        )

        self.names[unit["name"]] = obj

        for symbol in unit.get("symbols", []):
            self.symbols[symbol].add(obj)
            self.symbols_lower[symbol.lower()].add(obj)
            if unit["entity"] == "currency":
                self.prefix_symbols[symbol].add(obj)

        for surface in unit.get("surfaces", []):
            self.surfaces[surface].add(obj)
            self.surfaces_lower[surface.lower()].add(obj)
            plural = pluralize(surface, lang=self.lang)
            self.surfaces[plural].add(obj)
            self.surfaces_lower[plural.lower()].add(obj)

    @staticmethod
    def prefixed_units(unit):
        prefixed = []
        # If SI-prefixes are given, add them
        for prefix in unit.get("prefixes", []):
            assert (
                prefix in METRIC_PREFIXES
            ), "Given prefix '{}' for unit '{}' not supported".format(
                prefix, unit["name"]
            )
            assert (
                len(unit["dimensions"]) <= 1
            ), "Prefixing not supported for multiple dimensions in {}".format(
                unit["name"]
            )

            uri = METRIC_PREFIXES[prefix].capitalize() + unit["URI"].lower()
            # we usually do not want the "_(unit)" postfix for prefixed units
            uri = uri.replace("_(unit)", "")

            prefixed_unit = {
                "name": METRIC_PREFIXES[prefix] + unit["name"],
                "surfaces": [METRIC_PREFIXES[prefix] + i for i in unit["surfaces"]],
                "entity": unit["entity"],
                "URI": uri,
                "dimensions": [],
                "symbols": [prefix + i for i in unit["symbols"]],
            }
            prefixed.append(prefixed_unit)
        return prefixed


@cached
def units(lang="en_US"):
    """
    Cached unit object
    """
    return Units(lang)


###############################################################################
@cached
def training_set(lang="en_US"):
    training_set_ = []

    path = language.topdir(lang).joinpath("train")
    for file in path.iterdir():
        if file.suffix == ".json":
            with file.open("r", encoding="utf-8") as train_file:
                training_set_ += json.load(train_file)

    return training_set_
