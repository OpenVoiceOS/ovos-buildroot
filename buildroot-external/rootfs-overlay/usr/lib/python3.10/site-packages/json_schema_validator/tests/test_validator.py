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

import functools
import json
import sys

from testscenarios import TestWithScenarios
from testtools import TestCase

from json_schema_validator.errors import ValidationError
from json_schema_validator.shortcuts import validate
from json_schema_validator.validator import Validator

PY2 = sys.version_info[0] == 2
if PY2:
    import yaml

    def deserializer(json_string):
        # Always check the serialised JSON using the native JSON loader
        # so that any error messages are consistent and appropriate.
        json.loads(json_string)
        return yaml.safe_load(json_string)

    validate = functools.partial(validate, deserializer=deserializer)


class ValidatorFailureTests(TestWithScenarios, TestCase):

    scenarios = [
        ("type_string_got_null", {
            'schema': '{"type": "string"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_string_got_integer", {
            'schema': '{"type": "string"}',
            'data': '5',
            'raises': ValidationError(
                "5 does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_number_got_null", {
            'schema': '{"type": "number"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_number_got_string", {
            'schema': '{"type": "number"}',
            'data': '"foobar"',
            'raises': ValidationError(
                "'foobar' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_number_got_string_that_looks_like_number", {
            'schema': '{"type": "number"}',
            'data': '"3"',
            'raises': ValidationError(
                "'3' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_integer_got_float", {
            'schema': '{"type": "integer"}',
            'data': '1.5',
            'raises': ValidationError(
                "1.5 does not match type 'integer'",
                "Object has incorrect type (expected integer)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_integer_got_null", {
            'schema': '{"type": "integer"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'integer'",
                "Object has incorrect type (expected integer)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_null", {
            'schema': '{"type": "boolean"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_empty_string", {
            'schema': '{"type": "boolean"}',
            'data': '""',
            'raises': ValidationError(
                "'' does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_empty_list", {
            'schema': '{"type": "boolean"}',
            'data': '[]',
            'raises': ValidationError(
                "[] does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_boolean_got_empty_object", {
            'schema': '{"type": "boolean"}',
            'data': '{}',
            'raises': ValidationError(
                "{} does not match type 'boolean'",
                "Object has incorrect type (expected boolean)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_object_got_integer", {
            'schema': '{"type": "object"}',
            'data': '1',
            'raises': ValidationError(
                "1 does not match type 'object'",
                "Object has incorrect type (expected object)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_object_got_null", {
            'schema': '{"type": "object"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'object'",
                "Object has incorrect type (expected object)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_array_got_null", {
            'schema': '{"type": "array"}',
            'data': 'null',
            'raises': ValidationError(
                "None does not match type 'array'",
                "Object has incorrect type (expected array)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_array_got_integer", {
            'schema': '{"type": "array"}',
            'data': '1',
            'raises': ValidationError(
                "1 does not match type 'array'",
                "Object has incorrect type (expected array)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_empty_string", {
            'schema': '{"type": "null"}',
            'data': '""',
            'raises': ValidationError(
                "'' does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_zero", {
            'schema': '{"type": "null"}',
            'data': '0',
            'raises': ValidationError(
                "0 does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_empty_list", {
            'schema': '{"type": "null"}',
            'data': '[]',
            'raises': ValidationError(
                "[] does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_null_got_empty_object", {
            'schema': '{"type": "null"}',
            'data': '{}',
            'raises': ValidationError(
                "{} does not match type 'null'",
                "Object has incorrect type (expected null)"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("type_list_got_mismatching_item", {
            'schema': '{"type": ["string", "number"]}',
            'data': '{}',
            'raises': ValidationError(
                "{} does not match any of the types in ['string', 'number']",
                "Object has incorrect type (multiple types possible)",
                ".type"),
            'object_expr': 'object',
            'schema_expr': 'schema.type',
        }),
        ("property_check_is_not_primitive", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number"
                    }
                }
            }""",
            'data': '{"foo": "foobar"}',
            'raises': ValidationError(
                "'foobar' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object.foo',
            'schema_expr': 'schema.properties.foo.type',
        }),
        ("property_check_validates_optional_properties", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number",
                        "optional": true
                    }
                }
            }""",
            'data': '{"foo": null}',
            'raises': ValidationError(
                "None does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object.foo',
            'schema_expr': 'schema.properties.foo.type',
        }),
        ("property_check_reports_missing_non_optional_properties", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number",
                        "optional": false
                    }
                }
            }""",
            'data': '{}',
            'raises': ValidationError(
                "{} does not have property 'foo'",
                "Object lacks property 'foo'"),
            'object_expr': 'object',
            'schema_expr': 'schema.properties.foo.optional',
        }),
        ("property_check_reports_unknown_properties_when_additionalProperties_is_false", {
            'schema': """
            {
                "type": "object",
                "additionalProperties": false
            }""",
            'data': '{"foo": 5}',
            'raises': ValidationError(
                "{'foo': 5} has unknown property 'foo' and"
                " additionalProperties is false",
                "Object has unknown property 'foo' but additional "
                "properties are disallowed"),
            'object_expr': 'object',
            'schema_expr': 'schema.additionalProperties',
        }),
        ("property_check_validates_additional_properties_using_specified_type_when_additionalProperties_is_an_object_violation", {
            'schema': """
            {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                }
            }""",
            'data': '{"foo": "aaa", "bar": 5}',
            'raises': ValidationError(
                "5 does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object.bar',
            'schema_expr': 'schema.additionalProperties.type',
        }),
        ("enum_check_reports_unlisted_values", {
            'schema': '{"enum": [1, 2, 3]}',
            'data': '5',
            'raises': ValidationError(
                '5 does not match any value in enumeration [1, 2, 3]',
                "Object does not match any value in enumeration"),
            'object_expr': 'object',
            'schema_expr': 'schema.enum',
        }),
        ("items_with_single_schema_finds_problems", {
            'schema': '{"items": {"type": "string"}}',
            'data': '["foo", null, "froz"]',
            'raises': ValidationError(
                "None does not match type 'string'",
                "Object has incorrect type (expected string)"),
            'object_expr': 'object[1]',
            'schema_expr': 'schema.items.type',
        }),
        ("items_with_array_schema_checks_for_too_short_data", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ]
            }""",
            'data': '["foo"]',
            'raises': ValidationError(
                "['foo'] is shorter than array schema [{'type':"
                " 'string'}, {'type': 'boolean'}]",
                "Object array is shorter than schema array"),
            'object_expr': 'object',
            'schema_expr': 'schema.items',
        }),
        ("items_with_array_schema_and_additionalProperties_of_false_checks_for_too_much_data", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ],
                "additionalProperties": false
            }""",
            'data': '["foo", false, 5]',
            'raises': ValidationError(
                "['foo', False, 5] is not of the same length as array"
                " schema [{'type': 'string'}, {'type': 'boolean'}] and"
                " additionalProperties is false",
                "Object array is not of the same length as schema array"),
            'object_expr': 'object',
            'schema_expr': 'schema.items',
        }),
        ("items_with_array_schema_and_additionalProperties_can_find_problems", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ],
                "additionalProperties": {
                    "type": "number"
                }
            }""",
            'data': '["foo", false, 5, 7.9, null]',
            'raises': ValidationError(
                "None does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object[4]',
            'schema_expr': 'schema.additionalProperties.type',
        }),
        ("array_with_array_schema_and_uniqueItems_is_True", {
            'schema': """
            {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": true
            }""",
            'data': '["foo", "bar", "foo"]',
            'raises': ValidationError(
                "Repeated items found in ['foo', 'bar', 'foo']",
                "Repeated items found in array"),
            'object_expr': 'object',
            'schema_expr': 'schema.items',
        }),
        ("requires_with_simple_property_name_can_report_problems", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": "foo",
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"bar": null}',
            'raises': ValidationError(
                "None requires presence of property 'foo' in the same"
                " object",
                "Enclosing object does not have property 'foo'"),
            'object_expr': 'object.bar',
            'schema_expr': 'schema.properties.bar.requires',
        }),
        ("requires_with_simple_property_name_can_report_problems_while_nested", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "nested": {
                        "properties": {
                            "foo": {
                                "optional": true
                            },
                            "bar": {
                                "requires": "foo",
                                "optional": true
                            }
                        }
                    }
                }
            }
            """,
            'data': '{"nested": {"bar": null}}',
            'raises': ValidationError(
                "None requires presence of property 'foo' in the same"
                " object",
                "Enclosing object does not have property 'foo'"),
            'object_expr': 'object.nested.bar',
            'schema_expr': 'schema.properties.nested.properties.bar.requires',
        }),
        ("requires_with_schema_can_report_problems", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": {
                            "properties": {
                                "foo": {
                                    "type": "number"
                                }
                            }
                        },
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"bar": null}',
            'raises': ValidationError(
                "{'bar': None} does not have property 'foo'",
                "Object lacks property 'foo'"),
            'object_expr': 'object',
            'schema_expr': 'schema.properties.bar.requires.properties.foo.optional',
        }),
        ("requires_with_schema_can_report_subtle_problems", {
            # In this test presence of "bar" requires that "foo" is
            # present and has a type "number"
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": {
                            "properties": {
                                "foo": {
                                    "type": "number"
                                }
                            }
                        },
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"bar": null, "foo": "not a number"}',
            'raises': ValidationError(
                "'not a number' does not match type 'number'",
                "Object has incorrect type (expected number)"),
            'object_expr': 'object.foo',
            'schema_expr': 'schema.properties.bar.requires.properties.foo.type'
        }),
        ("format_date_time_finds_problems", {
            'schema': '{"format": "date-time"}',
            'data': '"broken"',
            'raises': ValidationError(
                "'broken' is not a string representing JSON date-time",
                "Object is not a string representing JSON date-time"),
            'object_expr': 'object',
            'schema_expr': 'schema.format'
        }),
    ]

    def test_validation_error_has_proper_message(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.message, self.raises.message)

    def test_validation_error_has_proper_new_message(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.new_message, self.raises.new_message)

    def test_validation_error_has_proper_object_expr(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.object_expr, self.object_expr)

    def test_validation_error_has_proper_schema_expr(self):
        ex = self.assertRaises(ValidationError,
                               validate, self.schema, self.data)
        self.assertEqual(ex.schema_expr, self.schema_expr)


class ValidatorSuccessTests(TestWithScenarios, TestCase):

    scenarios = [
        ("type_string_got_string", {
            'schema': '{"type": "string"}',
            'data': '"foobar"'
        }),
        ("type_number_got_integer", {
            'schema': '{"type": "number"}',
            'data': '1',
        }),
        ("type_number_number_float", {
            'schema': '{"type": "number"}',
            'data': '1.1',
        }),
        ("type_integer_got_integer_one", {
            'schema': '{"type": "integer"}',
            'data': '1'
        }),
        ("type_integer_got_integer", {
            'schema': '{"type": "integer"}',
            'data': '5'
        }),
        ("type_boolean_got_true", {
            'schema': '{"type": "boolean"}',
            'data': 'true',
        }),
        ("type_boolean_got_false", {
            'schema': '{"type": "boolean"}',
            'data': 'true',
        }),
        ("type_object_got_object", {
            'schema': '{"type": "object"}',
            'data': '{}'
        }),
        ("type_array_got_array", {
            'schema': '{"type": "array"}',
            'data': '[]'
        }),
        ("type_null_got_null", {
            'schema': '{"type": "null"}',
            'data': 'null',
        }),
        ("type_any_got_null", {
            'schema': '{"type": "any"}',
            'data': 'null',
        }),
        ("type_any_got_integer", {
            'schema': '{"type": "any"}',
            'data': '5',
        }),
        ("type_any_got_boolean", {
            'schema': '{"type": "any"}',
            'data': 'false',
        }),
        ("type_any_got_string", {
            'schema': '{"type": "any"}',
            'data': '"foobar"',
        }),
        ("type_any_got_array", {
            'schema': '{"type": "any"}',
            'data': '[]',
        }),
        ("type_any_got_object", {
            'schema': '{"type": "any"}',
            'data': '{}',
        }),
        ("type_nested_schema_check", {
            'schema': '{"type": {"type": "number"}}',
            'data': '5',
        }),
        ("type_list_with_two_values_got_first_value", {
            'schema': '{"type": ["number", "string"]}',
            'data': '1',
        }),
        ("type_list_with_two_values_got_second_value", {
            'schema': '{"type": ["number", "string"]}',
            'data': '"string"',
        }),
        ("property_ignored_on_non_objects", {
            'schema': '{"properties": {"foo": {"type": "number"}}}',
            'data': '"foobar"',
        }),
        ("property_checks_known_props", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number"
                    },
                    "bar": {
                        "type": "boolean"
                    }
                }
            }""",
            'data': """
            {
                "foo": 5,
                "bar": false
            }"""
        }),
        ("property_check_ignores_missing_optional_properties", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {
                        "type": "number",
                        "optional": true
                    }
                }
            }""",
            'data': '{}',
        }),
        ("property_check_ignores_normal_properties_when_additionalProperties_is_false", {
            'schema': """
            {
                "type": "object",
                "properties": {
                    "foo": {}
                },
                "additionalProperties": false
            }""",
            'data': '{"foo": 5}',
        }),
        ("property_check_validates_additional_properties_using_specified_type_when_additionalProperties_is_an_object", {
            'schema': """
            {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                }
            }""",
            'data': '{"foo": "aaa", "bar": "bbb"}',
        }),
        ("enum_check_does_nothing_by_default", {
            'schema': '{}',
            'data': '5',
        }),
        ("enum_check_verifies_possible_values", {
            'schema': '{"enum": [1, 2, 3]}',
            'data': '2',
        }),
        ("items_check_does_nothing_for_non_arrays", {
            'schema': '{"items": {"type": "string"}}',
            'data': '5',
        }),
        ("items_with_single_schema_applies_to_each_item", {
            'schema': '{"items": {"type": "string"}}',
            'data': '["foo", "bar", "froz"]',
        }),
        ("items_with_array_schema_applies_to_corresponding_items", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ]
            }""",
            'data': '["foo", true]',
        }),
        ("items_with_array_schema_and_additionalProperties", {
            'schema': """
            {
                "items": [
                    {"type": "string"},
                    {"type": "boolean"}
                ],
                "additionalProperties": {
                    "type": "number"
                }
            }""",
            'data': '["foo", false, 5, 7.9]',
        }),
        ("requires_with_simple_property_name_does_nothing_when_parent_property_is_not_used", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": "foo",
                        "optional": true
                    }
                }
            }
            """,
            'data': '{}',
        }),
        ("requires_with_simple_property_name_works_when_condition_satisfied", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": "foo",
                        "optional": true
                    }
                }
            }
            """,
            'data': '{"foo": null, "bar": null}',
        }),
        ("requires_with_schema_name_does_nothing_when_parent_property_is_not_used", {
            'schema': """
            {
                "properties": {
                    "foo": {
                        "optional": true
                    },
                    "bar": {
                        "requires": {
                            "properties": {
                                "foo": {
                                    "type": "number"
                                }
                            }
                        },
                        "optional": true
                    }
                }
            }
            """,
            'data': '{}',
        }),
        ("format_date_time_works", {
            'schema': '{"format": "date-time"}',
            'data': '"2010-11-12T14:38:55Z"',
        }),
        ("array_with_array_schema_and_uniqueItems_is_True", {
            'schema': """
            {
                "type": "array",
                "items": {"type": "string"},
                "uniqueItems": true
            }""",
            'data': '["foo", "bar", "baz"]',
        }),
    ]

    def test_validator_does_not_raise_an_exception(self):
        self.assertEqual(
            True, validate(self.schema, self.data))
