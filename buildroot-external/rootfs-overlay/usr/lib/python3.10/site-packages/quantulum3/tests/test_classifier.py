#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` tests.
"""

from __future__ import division

import json
import os
import unittest
import urllib.request

import joblib
import wikipedia

from .. import classifier as clf
from .. import language, load
from .. import parser as p
from .test_setup import (
    add_type_equalities,
    load_error_tests,
    load_expand_tests,
    load_quantity_tests,
    multilang,
)

COLOR1 = "\033[94m%s\033[0m"
COLOR2 = "\033[91m%s\033[0m"
TOPDIR = os.path.dirname(__file__) or "."


###############################################################################
class ClassifierBuild(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    @multilang
    def test_training(self, lang="en_US"):
        """ Test that classifier training works """
        # Test that no errors are thrown during training
        # Also stores result, to be included in package
        self.assertIsNotNone(clf.train_classifier(store=True, lang=lang))


###############################################################################
class ClassifierTest(unittest.TestCase):
    """Test suite for the quantulum3 project."""

    def setUp(self):
        add_type_equalities(self)

    @multilang
    def test_parse_classifier(self, lang="en_US"):
        """ Test that parsing works with classifier usage """
        # forcedly activate classifier
        clf.USE_CLF = True

        all_tests = load_quantity_tests(False, lang=lang)
        for test in sorted(all_tests, key=lambda x: len(x["req"])):
            with self.subTest(input=test["req"]):
                quants = p.parse(test["req"], lang=lang)

                self.assertEqual(
                    len(test["res"]),
                    len(quants),
                    msg="Differing amount of quantities parsed, expected {}, "
                    "got {}: {}, {}".format(
                        len(test["res"]), len(quants), test["res"], quants
                    ),
                )
                for index, quant in enumerate(quants):
                    self.assertEqual(quant, test["res"][index])

        classifier_tests = load_quantity_tests(True, lang)
        correct = 0
        total = len(classifier_tests)
        error = []
        for test in sorted(classifier_tests, key=lambda x: len(x["req"])):
            quants = p.parse(test["req"], lang=lang)
            if quants == test["res"]:
                correct += 1
            else:
                error.append((test, quants))
        success_rate = correct / total
        print("Classifier success rate at {:.2f}%".format(success_rate * 100))
        self.assertGreaterEqual(
            success_rate,
            0.8,
            "Classifier success rate was at {}%, below 80%.\nFailure at\n{}".format(
                success_rate * 100,
                "\n".join("{}: {}".format(test[0]["req"], test[1]) for test in error),
            ),
        )

    @multilang
    def test_expand(self, lang="en_US"):
        """ Test that parsing and expanding works correctly """
        all_tests = load_expand_tests(lang=lang)
        for test in all_tests:
            with self.subTest(input=test["req"]):
                result = p.inline_parse_and_expand(test["req"], lang=lang)
                self.assertEqual(result, test["res"])

    @multilang
    def test_errors(self, lang="en_US"):
        """ Test that no errors are thrown in edge cases """
        all_tests = load_error_tests(lang=lang)
        for test in all_tests:
            with self.subTest(input=test):
                # pylint: disable=broad-except
                try:
                    p.parse(test, lang=lang)
                except Exception as e:  # pragma: no cover
                    self.fail("Input caused an unhandled exception {}".format(e))

    @unittest.skip("Not necessary, as classifier is live built")
    @multilang
    def test_classifier_up_to_date(self, lang="en_US"):
        """
        Test that the classifier has been built with the latest version of
        scikit-learn
        """
        path = language.topdir(lang).joinpath("clf.joblib")
        with path.open("rb") as clf_file:
            obj = joblib.load(clf_file)
        clf_version = obj["scikit-learn_version"]
        with urllib.request.urlopen(
            "https://pypi.org/pypi/scikit-learn/json"
        ) as response:
            cur_version = json.loads(response.read().decode("utf-8"))["info"]["version"]
        self.assertEqual(
            clf_version,
            cur_version,
            "Classifier has been built with scikit-learn version {}, while the"
            " newest version is {}. Please update scikit-learn.".format(
                clf_version, cur_version
            ),
        )

    @unittest.skip("Skipped, as already run in build")
    @multilang
    def test_training(self, lang="en_US"):
        """ Test that classifier training works """
        # Test that no errors are thrown during training
        obj = clf.train_classifier(store=False, lang=lang)
        # Test that the classifier works with the currently downloaded data
        load._CACHE_DICT[id(clf.classifier)] = {
            lang: clf.Classifier(obj=obj, lang=lang)
        }
        self.test_parse_classifier(lang=lang)

    @multilang(["en_us"])
    def test_wikipedia_pages(self, lang):
        wikipedia.set_lang(lang[:2])
        err = []
        for unit in load.units(lang).names.values():
            try:
                wikipedia.page(unit.uri.replace("_", " "), auto_suggest=False)
                pass
            except (
                wikipedia.PageError,
                wikipedia.DisambiguationError,
            ) as e:  # pragma: no cover
                err.append((unit, e))
        if err:  # pragma: no cover
            self.fail("Problematic pages:\n{}".format("\n".join(str(e) for e in err)))


###############################################################################
if __name__ == "__main__":  # pragma: no cover
    unittest.main()
