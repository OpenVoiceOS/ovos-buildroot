#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

import json
import os
import re
import unittest
from typing import Dict, List

from .. import classes as cls
from .. import language, load
from .. import parser as p

try:
    import wikipedia
except ImportError:
    wikipedia = None


COLOR1 = "\033[94m%s\033[0m"
COLOR2 = "\033[91m%s\033[0m"
TOPDIR = os.path.dirname(__file__) or "."


def multilang(funct_or_langs):
    """
    Wrapper to make a unittest test several languages
    :param funct_or_langs: Function to test all languages or a set of languages
                           to test
    :return:
    """

    # The actual wrapper
    def multilang_(funct):
        def multilang_test(*args, **kwargs):
            print()
            # Allow for someone to call the method with one explicit language
            if "lang" in kwargs:
                langs_ = [kwargs["lang"]]
                kwargs.pop("lang")
            else:
                langs_ = langs

            # Execute the test for all the supplied languages
            for lang in langs_:
                print("lang={}".format(lang))
                funct(*args, lang=lang, **kwargs)

        return multilang_test

    # Decide whether we *are* the wrapper or are to create it
    if callable(funct_or_langs):
        langs = language.LANGUAGES
        return multilang_(funct_or_langs)

    langs = funct_or_langs
    return multilang_


def add_type_equalities(testcase):
    """
    Add handcrafted equality functions for quantulum specific types
    :param testcase:
    :return:
    """

    def quantity_equality_func(first, second, msg=None):
        if first != second:
            if not msg:
                diffs = {"value", "surface", "span", "uncertainty"}
                for diff in diffs:
                    firstval = getattr(first, diff)
                    secondval = getattr(second, diff)
                    if firstval != secondval:
                        msg = (
                            "Quantities {first} and {second} are differing "
                            'in attribute "{attribute}":'
                            "{firstval} != {secondval}"
                        )
                        msg = msg.format(
                            attribute=diff,
                            firstval=firstval,
                            secondval=secondval,
                            first=first,
                            second=second,
                        )
                        break
            if not msg:
                if first.unit != second.unit:
                    msg = "Quantity units are differing:\n{}\n{}".format(
                        first.unit.__dict__, second.unit.__dict__
                    )
            raise testcase.failureException(msg)

    testcase.addTypeEqualityFunc(cls.Quantity, quantity_equality_func)


###############################################################################
def wiki_test(page="CERN", lang="en_US"):  # pragma: no cover
    """
    Download a wikipedia page and test the parser on its content.
    A test, designed for a human's look.
    Pages full of units:
        CERN
        Hubble_Space_Telescope,
        Herschel_Space_Observatory
    """
    if not wikipedia:
        print(
            "Cannot activate wiki_test. Please install the package wikipedia " "first."
        )
        return

    wikipedia.set_lang(lang)
    content = wikipedia.page(page).content
    parsed = p.parse(content, lang=lang)
    parts = int(round(len(content) * 1.0 / 1000))

    print()
    end_char = 0
    for num, chunk in enumerate(range(parts)):
        os.system("clear")
        print()
        qua = [j for j in parsed if chunk * 1000 < j.span[0] < (chunk + 1) * 1000]
        beg_char = max(chunk * 1000, end_char)
        if qua:
            end_char = max((chunk + 1) * 1000, qua[-1].span[1])
            text = content[beg_char:end_char]
            shift = 0
            for quantity in qua:
                index = quantity.span[1] - beg_char + shift
                to_add = COLOR1 % (" {" + str(quantity) + "}")
                text = text[0:index] + to_add + COLOR2 % text[index:]
                shift += len(to_add) + len(COLOR2) - 6
        else:
            text = content[beg_char : (chunk + 1) * 1000]
        print(COLOR2 % text)
        print()
        try:
            input("--------- End part %d of %d\n" % (num + 1, parts))
        except (KeyboardInterrupt, EOFError):
            return


###############################################################################
def load_quantity_tests(ambiguity=True, lang="en_US"):
    """
    Load all tests from quantities.json.
    """

    path = language.topdir(lang).joinpath(
        "tests", "quantities.ambiguity.json" if ambiguity else "quantities.json"
    )
    with path.open("r", encoding="UTF-8") as testfile:
        tests = json.load(testfile)

    for test in tests:
        res = []
        for item in test["res"]:
            try:
                unit = load.units(lang).names[item["unit"]]
            except KeyError:
                try:
                    entity = item["entity"]
                except KeyError:  # pragma: no cover
                    print(
                        (
                            'Could not find %s, provide "derived" and'
                            ' "entity"' % item["unit"]
                        )
                    )
                    return
                if entity == "unknown":
                    derived = [
                        {
                            "base": load.units(lang).names[i["base"]].entity.name,
                            "power": i["power"],
                        }
                        for i in item["dimensions"]
                    ]
                    entity = cls.Entity(name="unknown", dimensions=derived)
                elif entity in load.entities(lang).names:
                    entity = load.entities(lang).names[entity]
                else:  # pragma: no cover
                    print(
                        (
                            'Could not find %s, provide "derived" and'
                            ' "entity"' % item["unit"]
                        )
                    )
                    return
                unit = cls.Unit(
                    name=item["unit"],
                    dimensions=item.get("dimensions", []),
                    entity=entity,
                    lang=lang,
                )
            try:
                # TODO be aware that there may never be two identical units in
                # a req string
                span = next(re.finditer(re.escape(item["surface"]), test["req"])).span()
            except StopIteration:  # pragma: no cover
                print('Surface mismatch for "%s"' % test["req"])
                return
            uncert = None
            if "uncertainty" in item:
                uncert = item["uncertainty"]
            res.append(
                cls.Quantity(
                    value=item["value"],
                    unit=unit,
                    surface=item["surface"],
                    span=span,
                    uncertainty=uncert,
                    lang=lang,
                )
            )
        test["res"] = [i for i in res]

    return tests


###############################################################################
def load_expand_tests(lang="en_US") -> List[Dict[str, str]]:
    with language.topdir(lang).joinpath("tests", "expand.json").open(
        "r", encoding="utf-8"
    ) as testfile:
        tests = json.load(testfile)
    return tests


###############################################################################
def load_error_tests(lang="en_US") -> List[str]:
    with language.topdir(lang).joinpath("tests", "errors.json").open(
        "r", encoding="utf-8"
    ) as testfile:
        tests = json.load(testfile)
    return tests


###############################################################################
class SetupTest(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    def setUp(self):
        add_type_equalities(self)

    @multilang
    def test_load_tests(self, lang="en_US"):
        """ Test that loading tests works """
        self.assertIsNotNone(load_quantity_tests(True, lang))
        self.assertIsNotNone(load_quantity_tests(False, lang))
        self.assertIsNotNone(load_expand_tests(lang))
        self.assertIsNotNone(load_error_tests(lang))

    @unittest.expectedFailure
    def test_quantity_comparison_fail_unit(self):
        """ Test unequal units (differing only in their entity) """
        self.assertEqual(
            cls.Quantity(1, cls.Unit(entity=cls.Entity("water"))),
            cls.Quantity(1, cls.Unit(entity=cls.Entity("air"))),
        )

    @unittest.expectedFailure
    def test_quantity_comparison_fail_value(self):
        """ Test unequal units (differing only in their value) """
        self.assertEqual(
            cls.Quantity(1, cls.Unit(entity=cls.Entity("water"))),
            cls.Quantity(2, cls.Unit(entity=cls.Entity("water"))),
        )

    def test_unsupported_language(self):
        """ Test if unknown langugage fails """
        try:
            p.parse("Urgh wooo ddaa eeee!", lang="xx")
            self.fail("No error was thrown on unsupported language")  # pragma: no cover
        except NotImplementedError:
            pass

    @multilang(["en_US"])
    def test_common_words(self, lang):
        """ Test that the build script has run correctly (*might* fail locally) """
        # Read raw 4 letter file
        words = language.get("load", lang).build_common_words()
        built = language.get("load", lang).COMMON_WORDS
        for length, word_list in built.items():
            self.assertEqual(
                words[length],
                word_list,
                "Build script has not been run since change to critical files",
            )


###############################################################################
if __name__ == "__main__":  # pragma: no cover

    unittest.main()
