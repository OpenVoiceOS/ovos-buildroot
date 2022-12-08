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
Unit tests for JSON schema
"""

import json
import sys

from testscenarios import TestWithScenarios
from testtools import TestCase

from json_schema_validator.errors import SchemaError
from json_schema_validator.schema import Schema

PY2 = sys.version_info[0] == 2
PY35 = sys.version_info[0:2] >= (3, 5)

if PY2:
    import yaml
    deserializer = yaml.safe_load
else:
    deserializer = json.loads


class SchemaTests(TestWithScenarios, TestCase):

    scenarios = [
        ('type_default', {
            'schema': '{}',
            'expected': {
                'type': 'any'
            },
        }),
        ('type_string', {
            'schema': '{"type": "string"}',
            'expected': {
                'type': 'string'
            },
        }),
        ('type_number', {
            'schema': '{"type": "number"}',
            'expected': {
                'type': 'number'
            },
        }),
        ('type_integer', {
            'schema': '{"type": "integer"}',
            'expected': {
                'type': 'integer'
            },
        }),
        ('type_boolean', {
            'schema': '{"type": "boolean"}',
            'expected': {
                'type': 'boolean'
            },
        }),
        ('type_object', {
            'schema': '{"type": "object"}',
            'expected': {
                'type': 'object'
            },
        }),
        ('type_array', {
            'schema': '{"type": "array"}',
            'expected': {
                'type': 'array'
            },
        }),
        ('type_complex_subtype', {
            'schema': '{"type": {}}',
            'expected': {
                'type': {},
            },
        }),
        ("type_empty_list", {
            'schema': '{"type": []}',
            'access': 'type',
            'raises': SchemaError("union type [] is too short")
        }),
        ("type_list_with_one_item", {
            'schema': '{"type": ["number"]}',
            'access': 'type',
            'raises': SchemaError("union type ['number'] is too short")
        }),
        ('type_list', {
            'schema': '{"type": ["string", "number"]}',
            'expected': {
                'type': ["string", "number"],
            },
        }),
        ('type_wrong_type', {
            'schema': '{"type": 5}',
            'access': 'type',
            'raises': SchemaError(
                "type value 5 is not a simple type name,"
                " nested schema nor a list of those"),
        }),
        ('type_not_a_simple_type_name', {
            'schema': '{"type": "foobar"}',
            'access': 'type',
            'raises': SchemaError(
                "type value 'foobar' is not a simple type name"),
        }),
        ('type_list_duplicates', {
            'schema': '{"type": ["string", "string"]}',
            'access': 'type',
            'raises': SchemaError(
                "type value ['string', 'string'] contains duplicate"
                " element 'string'")
        }),
        ('properties_default', {
            'schema': '{}',
            'expected': {
                'properties': {},
            },
        }),
        ('properties_example', {
            'schema': '{"properties": {"prop": {"type": "number"}}}',
            'expected': {
                'properties': {"prop": {"type": "number"}},
            },
        }),
        ('properties_wrong_type', {
            'schema': '{"properties": 5}',
            'access': 'properties',
            'raises': SchemaError(
                'properties value 5 is not an object'),
        }),
        ('items_default', {
            'schema': '{}',
            'expected': {
                'items': {},
            },
        }),
        ('items_tuple', {
            'schema': '{"items": [{}, {}]}',
            'expected': {
                'items': [{}, {}],
            },
        }),
        ('items_each', {
            'schema': '{"items": {"type": "number"}}',
            'expected': {
                'items': {"type": "number"},
            },
        }),
        ('items_wrong_type', {
            'schema': '{"items": 5}',
            'access': 'items',
            'raises': SchemaError(
                'items value 5 is neither a list nor an object'),
        }),
        ('optional_default', {
            'schema': '{}',
            'expected': {
                'optional': False,
            },
        }),
        ('optional_true', {
            'schema': '{"optional": true}',
            'expected': {
                'optional': True,
            },
        }),
        ('optional_false', {
            'schema': '{"optional": false}',
            'expected': {
                'optional': False,
            },
        }),
        ('optional_wrong_type', {
            'schema': '{"optional": 5}',
            'access': 'optional',
            'raises': SchemaError(
                'optional value 5 is not a boolean'),
        }),
        ('additionalProperties_default', {
            'schema': '{}',
            'expected': {
                'additionalProperties': {}
            },
        }),
        ('additionalProperties_false', {
            'schema': '{"additionalProperties": false}',
            'expected': {
                "additionalProperties": False,
            },
        }),
        ('additionalProperties_object', {
            'schema': '{"additionalProperties": {"type": "number"}}',
            'expected': {
                "additionalProperties": {"type": "number"},
            },
        }),
        ('additionalProperties_wrong_type', {
            'schema': '{"additionalProperties": 5}',
            'access': 'additionalProperties',
            'raises': SchemaError(
                'additionalProperties value 5 is neither false nor an'
                ' object'),
        }),
        ('requires_default', {
            'schema': '{}',
            'expected': {
                'requires': {},
            },
        }),
        ('requires_property_name', {
            'schema': '{"requires": "other"}',
            'expected': {
                'requires': "other",
            },
        }),
        ('requires_schema', {
            'schema': '{"requires": {"properties": {"other": {"type": "number"}}}}',
            'expected': {
                'requires': {
                    'properties': {
                        'other': {
                            'type': 'number'
                        },
                    },
                },
            },
        }),
        ('requires_wrong_value', {
            'schema': '{"requires": 5}',
            'access': 'requires',
            'raises': SchemaError(
                'requires value 5 is neither a string nor an object'),
        }),
        ('minimum_default', {
            'schema': '{}',
            'expected': {
                'minimum': None
            },
        }),
        ('minimum_integer', {
            'schema': '{"minimum": 5}',
            'expected': {
                'minimum': 5
            },
        }),
        ('minimum_float', {
            'schema': '{"minimum": 3.5}',
            'expected': {
                'minimum': 3.5
            },
        }),
        ('minimum_wrong_type', {
            'schema': '{"minimum": "foobar"}',
            'access': 'minimum',
            'raises': SchemaError(
                'minimum value \'foobar\' is not a numeric type')
        }),
        ('maximum_default', {
            'schema': '{}',
            'expected': {
                'maximum': None
            },
        }),
        ('maximum_integer', {
            'schema': '{"maximum": 5}',
            'expected': {
                'maximum': 5
            },
        }),
        ('maximum_float', {
            'schema': '{"maximum": 3.5}',
            'expected': {
                'maximum': 3.5
            },
        }),
        ('maximum_wrong_type', {
            'schema': '{"maximum": "foobar"}',
            'access': 'maximum',
            'raises': SchemaError(
                'maximum value \'foobar\' is not a numeric type')
        }),
        ('minimumCanEqual_default', {
            'schema': '{"minimum": 5}',
            'expected': {
                'minimum': 5,
                'minimumCanEqual': True
            },
        }),
        ('minimumCanEqual_false', {
            'schema': '{"minimum": 5, "minimumCanEqual": false}',
            'expected': {
                'minimum': 5,
                'minimumCanEqual': False,
            },
        }),
        ('minimumCanEqual_true', {
            'schema': '{"minimum": 5, "minimumCanEqual": true}',
            'expected': {
                'minimum': 5,
                'minimumCanEqual': True
            },
        }),
        ('minimumCanEqual_without_minimum', {
            'schema': '{}',
            'access': 'minimumCanEqual',
            'raises': SchemaError(
                "minimumCanEqual requires presence of minimum"),
        }),
        ('minimumCanEqual_wrong_type', {
            'schema': '{"minimum": 5, "minimumCanEqual": 5}',
            'access': 'minimumCanEqual',
            'raises': SchemaError(
                "minimumCanEqual value 5 is not a boolean"),
        }),
        ('maximumCanEqual_default', {
            'schema': '{"maximum": 5}',
            'expected': {
                'maximum': 5,
                'maximumCanEqual': True
            },
        }),
        ('maximumCanEqual_false', {
            'schema': '{"maximum": 5, "maximumCanEqual": false}',
            'expected': {
                'maximum': 5,
                'maximumCanEqual': False,
            },
        }),
        ('maximumCanEqual_true', {
            'schema': '{"maximum": 5, "maximumCanEqual": true}',
            'expected': {
                'maximum': 5,
                'maximumCanEqual': True
            },
        }),
        ('maximumCanEqual_without_maximum', {
            'schema': '{}',
            'access': 'maximumCanEqual',
            'raises': SchemaError(
                "maximumCanEqual requires presence of maximum"),
        }),
        ('maximumCanEqual_wrong_type', {
            'schema': '{"maximum": 5, "maximumCanEqual": 5}',
            'access': 'maximumCanEqual',
            'raises': SchemaError(
                "maximumCanEqual value 5 is not a boolean"),
        }),
        ("minItems_default", {
            'schema': '{}',
            'expected': {
                'minItems': 0,
            },
        }),
        ("minItems_integer", {
            'schema': '{"minItems": 13}',
            'expected': {
                'minItems': 13,
            },
        }),
        ("minItems_zero", {
            'schema': '{"minItems": 0}',
            'expected': {
                'minItems': 0,
            },
        }),
        ("minItems_minus_one", {
            'schema': '{"minItems": -1}',
            'access': 'minItems',
            'raises': SchemaError(
                "minItems value -1 cannot be negative"),
        }),
        ("minItems_wrong_type", {
            'schema': '{"minItems": "foobar"}',
            'access': 'minItems',
            'raises': SchemaError(
                "minItems value 'foobar' is not an integer"),
        }),
        ("maxItems_default", {
            'schema': '{}',
            'expected': {
                'maxItems': None,
            },
        }),
        ("maxItems_integer", {
            'schema': '{"maxItems": 13}',
            'expected': {
                'maxItems': 13,
            },
        }),
        ("maxItems_zero", {
            'schema': '{"maxItems": 0}',
            'expected': {
                'maxItems': 0,
            },
        }),
        ("maxItems_minus_one", {
            'schema': '{"maxItems": -1}',
            'expected': {
                'maxItems': -1
            },
        }),
        ("maxItems_wrong_type", {
            'schema': '{"maxItems": "foobar"}',
            'access': 'maxItems',
            'raises': SchemaError(
                "maxItems value 'foobar' is not an integer"),
        }),
        ("uniqueItems_default", {
            'schema': '{}',
            'expected': {
                'uniqueItems': False
            }
        }),
        ("uniqueItems_true", {
            'schema': '{"uniqueItems": true}',
            'expected': {
                'uniqueItems': True
            }
        }),
        ("uniqueItems_false", {
            'schema': '{"uniqueItems": false}',
            'expected': {
                'uniqueItems': False
            }
        }),
        ("uniqueItems_wrong_type", {
            'schema': '{"uniqueItems": 5}',
            'access': 'uniqueItems',
            'raises': SchemaError(
                "uniqueItems value 5 is not a boolean")
        }),
        ("pattern_default", {
            'schema': '{}',
            'expected': {
                'pattern': None,
            },
        }),
        #("pattern_simple", {
        #    'schema': '{"pattern": "foo|bar"}',
        #    'expected': {
        #        'pattern': re.compile('foo|bar'),
        #    },
        #}),
        ("pattern_broken", {
            'schema': '{"pattern": "[unterminated"}',
            'access': 'pattern',
            'raises': SchemaError(
                "pattern value '[unterminated' is not a valid regular"
                " expression: " +
                ("unexpected end of regular expression" if not PY35 else
                 "unterminated character set at position 0"
                 )),
        }),
        ("minLength_default", {
            'schema': '{}',
            'expected': {
                'minLength': 0,
            },
        }),
        ("minLength_integer", {
            'schema': '{"minLength": 13}',
            'expected': {
                'minLength': 13,
            },
        }),
        ("minLength_zero", {
            'schema': '{"minLength": 0}',
            'expected': {
                'minLength': 0,
            },
        }),
        ("minLength_minus_one", {
            'schema': '{"minLength": -1}',
            'access': 'minLength',
            'raises': SchemaError(
                "minLength value -1 cannot be negative"),
        }),
        ("minLength_wrong_type", {
            'schema': '{"minLength": "foobar"}',
            'access': 'minLength',
            'raises': SchemaError(
                "minLength value 'foobar' is not an integer"),
        }),
        ("maxLength_default", {
            'schema': '{}',
            'expected': {
                'maxLength': None,
            },
        }),
        ("maxLength_integer", {
            'schema': '{"maxLength": 13}',
            'expected': {
                'maxLength': 13,
            },
        }),
        ("maxLength_zero", {
            'schema': '{"maxLength": 0}',
            'expected': {
                'maxLength': 0,
            },
        }),
        ("maxLength_minus_one", {
            'schema': '{"maxLength": -1}',
            'expected': {
                'maxLength': -1
            },
        }),
        ("maxLength_wrong_type", {
            'schema': '{"maxLength": "foobar"}',
            'access': 'maxLength',
            'raises': SchemaError(
                "maxLength value 'foobar' is not an integer"),
        }),
        ("enum_default", {
            'schema': '{}',
            'expected': {
                'enum': None,
            }
        }),
        ("enum_simple", {
            'schema': '{"enum": ["foo", "bar"]}',
            'expected': {
                'enum': ["foo", "bar"],
            }
        }),
        ("enum_mixed", {
            'schema': '{"enum": [5, false, "foobar"]}',
            'expected': {
                'enum':[5, False, "foobar"]
            }
        }),
        ("enum_wrong_type", {
            'schema': '{"enum": "foobar"}',
            'access': 'enum',
            'raises': SchemaError(
                "enum value 'foobar' is not a list"),
        }),
        ("enum_too_short", {
            'schema': '{"enum": []}',
            'access': 'enum',
            'raises': SchemaError(
                "enum value [] does not contain any elements"),
        }),
        ("enum_duplicates", {
            'schema': '{"enum": ["foo", "foo"]}',
            'access': 'enum',
            'raises': SchemaError(
                "enum value ['foo', 'foo'] contains duplicate element"
                " 'foo'"),
        }),
        ("title_default", {
            'schema': '{}',
            'expected': {
                'title': None,
            },
        }),
        ("title_simple", {
            'schema': '{"title": "foobar"}',
            'expected': {
                'title': "foobar",
            },
        }),
        ("title_wrong_type", {
            'schema': '{"title": 5}',
            'access': 'title',
            'raises': SchemaError('title value 5 is not a string')
        }),
        ("description_default", {
            'schema': '{}',
            'expected': {
                'description': None,
            },
        }),
        ("description_simple", {
            'schema': '{"description": "foobar"}',
            'expected': {
                'description': "foobar",
            },
        }),
        ("description_wrong_type", {
            'schema': '{"description": 5}',
            'access': 'description',
            'raises': SchemaError('description value 5 is not a string')
        }),
        ("format_default", {
            'schema': '{}',
            'expected': {
                'format': None
            },
        }),
        ("format_date_time", {
            'schema': '{"format": "date-time"}',
            'expected': {
                'format': "date-time"
            },
        }),
        ("format_regex", {
            'schema': '{"format": "regex"}',
            'expected': {
                'format': "regex"
            },
        }),
        ("format_wrong_type", {
            'schema': '{"format": 5}',
            'access': 'format',
            'raises': SchemaError('format value 5 is not a string')
        }),
        ("format_not_implemented", {
            'schema': '{"format": "color"}',
            'access': 'format',
            'raises': NotImplementedError(
                "format value 'color' is not supported")
        }),
        ("contentEncoding_default", {
            'schema': '{}',
            'expected': {
                'contentEncoding': None,
            }
        }),
        ("contentEncoding_base64", {
            'schema': '{"contentEncoding": "base64"}',
            'expected': {
                'contentEncoding': "base64",
            },
        }),
        ("contentEncoding_base64_mixed_case", {
            'schema': '{"contentEncoding": "BAsE64"}',
            'expected': {
                'contentEncoding': 'BAsE64',
            },
        }),
        ("contentEncoding_unsupported_value", {
            'schema': '{"contentEncoding": "x-token"}',
            'access': 'contentEncoding',
            'raises': NotImplementedError(
                "contentEncoding value 'x-token' is not supported")
        }),
        ("contentEncoding_unknown_value", {
            'schema': '{"contentEncoding": "bogus"}',
            'access': 'contentEncoding',
            'raises': SchemaError(
                "contentEncoding value 'bogus' is not valid")
        }),
        ("divisibleBy_default", {
            'schema': '{}',
            'expected': {
                'divisibleBy': 1
            }
        }),
        ("divisibleBy_int", {
            'schema': '{"divisibleBy": 5}',
            'expected': {
                'divisibleBy': 5
            }
        }),
        ("divisibleBy_float", {
            'schema': '{"divisibleBy": 3.5}',
            'expected': {
                'divisibleBy': 3.5
            }
        }),
        ("divisibleBy_wrong_type", {
            'schema': '{"divisibleBy": "foobar"}',
            'access': 'divisibleBy',
            'raises': SchemaError(
                "divisibleBy value 'foobar' is not a numeric type")
        }),
        ("divisibleBy_minus_one", {
            'schema': '{"divisibleBy": -1}',
            'access': 'divisibleBy',
            'raises': SchemaError(
                "divisibleBy value -1 cannot be negative")
        }),
        ('disallow_default', {
            'schema': '{}',
            'expected': {
                'disallow': None
            },
        }),
        ('disallow_string', {
            'schema': '{"disallow": "string"}',
            'expected': {
                'disallow': ['string']
            },
        }),
        ('disallow_number', {
            'schema': '{"disallow": "number"}',
            'expected': {
                'disallow': ['number']
            },
        }),
        ('disallow_integer', {
            'schema': '{"disallow": "integer"}',
            'expected': {
                'disallow': ['integer']
            },
        }),
        ('disallow_boolean', {
            'schema': '{"disallow": "boolean"}',
            'expected': {
                'disallow': ['boolean']
            },
        }),
        ('disallow_object', {
            'schema': '{"disallow": "object"}',
            'expected': {
                'disallow': ['object']
            },
        }),
        ('disallow_array', {
            'schema': '{"disallow": "array"}',
            'expected': {
                'disallow': ['array']
            },
        }),
        ('disallow_complex_subtype', {
            'schema': '{"disallow": {}}',
            'expected': {
                'disallow': [{}],
            },
        }),
        ('disallow_list', {
            'schema': '{"disallow": ["string", "number"]}',
            'expected': {
                'disallow': ["string", "number"],
            },
        }),
        ('disallow_wrong_type', {
            'schema': '{"disallow": 5}',
            'access': 'disallow',
            'raises': SchemaError(
                "disallow value 5 is not a simple type name,"
                " nested schema nor a list of those"),
        }),
        ('disallow_not_a_simple_disallow_name', {
            'schema': '{"disallow": "foobar"}',
            'access': 'disallow',
            'raises': SchemaError(
                "disallow value 'foobar' is not a simple type name")
        }),
        ('disallow_list_duplicates', {
            'schema': '{"disallow": ["string", "string"]}',
            'access': 'disallow',
            'raises': SchemaError(
                "disallow value ['string', 'string'] contains"
                " duplicate element 'string'")
        }),
        ('extends_not_supported', {
            'schema': '{}',
            'access': 'extends',
            'raises': NotImplementedError(
                "extends property is not supported"),
        }),
        ('default_with_value', {
            'schema': '{"default": 5}',
            'expected': {
                'default': 5
            }
        }),
        ('default_without_value', {
            'schema': '{}',
            'access': 'default',
            'raises': SchemaError("There is no schema default for this item"),
        }),
    ]

    def test_schema_attribute(self):
        if deserializer != json.loads:
            # Always check the serialised JSON using the native JSON loader
            # so that any error messages are consistent and appropriate.
            json.loads(self.schema)

        schema = Schema(deserializer(self.schema))
        if hasattr(self, 'expected'):
            for attr, expected_value in self.expected.items():
                self.assertEqual(
                    expected_value, getattr(schema, attr))
        elif hasattr(self, 'access') and hasattr(self, 'raises'):
            self.assertRaises(
                type(self.raises),
                getattr, schema, self.access)
            try:
                getattr(schema, self.access)
            except type(self.raises) as ex:
                self.assertEqual(str(ex), str(self.raises))
            except Exception as ex:
                self.fail("Raised exception {0!r} instead of {1!r}".format(
                    ex, self.raises))
        else:
            self.fail("Broken test definition, must define 'expected' "
                      "or 'access' and 'raises' scenario attributes")
