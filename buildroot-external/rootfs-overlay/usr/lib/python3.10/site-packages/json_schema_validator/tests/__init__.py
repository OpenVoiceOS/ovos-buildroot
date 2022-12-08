# Copyright (C) 2010, 2011 Linaro Limited
# Copyright (C) 2016 Zygmunt Krynicki
#
# Author: Zygmunt Krynicki <me@zygoon.pl>
#
# This file is part of json-schema-validator.
#
# json-schema-validator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# json-schema-validator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with json-schema-validator.  If not, see <http://www.gnu.org/licenses/>.

"""
Package with unit tests for json-schema-validator
"""

import doctest
import unittest


def app_modules():
    return [
        'json_schema_validator',
        'json_schema_validator.errors',
        'json_schema_validator.extensions',
        'json_schema_validator.misc',
        'json_schema_validator.schema',
        'json_schema_validator.shortcuts',
        'json_schema_validator.validator',
    ]


def test_modules():
    return [
        'json_schema_validator.tests.test_extensions',
        'json_schema_validator.tests.test_schema',
        'json_schema_validator.tests.test_validator',
    ]


def test_suite():
    """
    Build an unittest.TestSuite() object with all the tests in _modules.
    Each module is harvested for both regular unittests and doctests
    """
    modules = app_modules() + test_modules()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in modules:
        __import__(name, fromlist=[''])
        tests = loader.loadTestsFromName(name)
        suite.addTests(tests)
        doctests = doctest.DocTestSuite(name)
        suite.addTests(doctests)
    return suite
