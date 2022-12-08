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
Unit tests for JSON extensions
"""

from testtools import TestCase
from datetime import datetime, timedelta

from json_schema_validator.extensions import datetime_extension, timedelta_extension


class ExtensionTests(object):

    def test_to_json(self):
        text = self.extension.to_json(self.reference_obj)
        self.assertEqual(text, self.reference_text)

    def test_from_json(self):
        obj = self.extension.from_json(self.reference_text)
        self.assertEqual(obj, self.reference_obj)


class DatetimeExtensionTests(TestCase, ExtensionTests):

    reference_obj = datetime(2010, 12, 7, 23, 59, 58)
    reference_text = "2010-12-07T23:59:58Z"
    extension = datetime_extension


class TimedeltaExtensionTests(TestCase, ExtensionTests):

    reference_obj = timedelta(days=1, seconds=2, microseconds=3)
    reference_text = "1d 2s 3us"
    extension = timedelta_extension
