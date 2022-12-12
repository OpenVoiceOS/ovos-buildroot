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

"""Validator implementation."""

import re
import datetime
import itertools
import types
import sys

from json_schema_validator.errors import ValidationError
from json_schema_validator.misc import NUMERIC_TYPES
from json_schema_validator.schema import Schema

if sys.version_info[0] > 2:
    basestring = (str, )
    zip_longest = itertools.zip_longest
else:
    zip_longest = itertools.izip_longest


class Validator(object):
    """
    JSON Schema validator.

    Can be used to validate any JSON document against a
    :class:`json_schema_validator.schema.Schema`.
    """

    JSON_TYPE_MAP = {
        "string": basestring,
        "number": NUMERIC_TYPES,
        "integer": int,
        "object": dict,
        "array": list,
        "null": None.__class__,
    }

    def __init__(self):
        self._schema_stack = []
        self._object_stack = []

    def _push_object(self, obj, path):
        self._object_stack.append((obj, path))

    def _pop_object(self):
        self._object_stack.pop()

    def _push_schema(self, schema, path):
        self._schema_stack.append((schema, path))

    def _pop_schema(self):
        self._schema_stack.pop()

    @property
    def _object(self):
        return self._object_stack[-1][0]

    @property
    def _schema(self):
        return self._schema_stack[-1][0]

    @classmethod
    def validate(cls, schema, obj):
        """
        Validate specified JSON object obj with specified schema.

        :param schema:
            Schema to validate against
        :type schema:
            :class:`json_schema_validator.schema.Schema`
        :param obj:
            JSON object to validate
        :rtype:
            bool
        :returns:
            True on success
        :raises `json_schema_validator.errors.ValidationError`:
            if the object does not match schema.
        :raises `json_schema_validator.errors.SchemaError`:
            if the schema itself is wrong.
        """
        if not isinstance(schema, Schema):
            raise ValueError(
                "schema value {0!r} is not a Schema"
                " object".format(schema))
        self = cls()
        self.validate_toplevel(schema, obj)
        return True

    def _get_object_expression(self):
        return "".join(map(lambda x: x[1], self._object_stack))

    def _get_schema_expression(self):
        return "".join(map(lambda x: x[1], self._schema_stack))

    def validate_toplevel(self, schema, obj):
        self._object_stack = []
        self._schema_stack = []
        self._push_schema(schema, "schema")
        self._push_object(obj, "object")
        self._validate()
        self._pop_schema()
        self._pop_object()

    def _validate(self):
        obj = self._object
        self._validate_type()
        self._validate_requires()
        if isinstance(obj, dict):
            self._validate_properties()
            self._validate_additional_properties()
        elif isinstance(obj, list):
            self._validate_items()
        else:
            self._validate_enum()
            self._validate_format()
            self._validate_pattern()
            if isinstance(obj, basestring):
                self._validate_length()
            elif isinstance(obj, NUMERIC_TYPES):
                self._validate_range()
        self._report_unsupported()

    def _report_error(self, legacy_message, new_message=None,
                      schema_suffix=None):
        """
        Report an error during validation.

        There are two error messages. The legacy message is used for backwards
        compatibility and usually contains the object (possibly very large)
        that failed to validate. The new message is much better as it contains
        just a short message on what went wrong. User code can inspect
        object_expr and schema_expr to see which part of the object failed to
        validate against which part of the schema.

        The schema_suffix, if provided, is appended to the schema_expr.  This
        is quite handy to specify the bit that the validator looked at (such as
        the type or optional flag, etc). object_suffix serves the same purpose
        but is used for object expressions instead.
        """
        object_expr = self._get_object_expression()
        schema_expr = self._get_schema_expression()
        if schema_suffix:
            schema_expr += schema_suffix
        raise ValidationError(legacy_message, new_message, object_expr,
                              schema_expr)

    def _push_property_schema(self, prop):
        """Construct a sub-schema from a property of the current schema."""
        schema = Schema(self._schema.properties[prop])
        self._push_schema(schema, ".properties." + prop)

    def _push_additional_property_schema(self):
        schema = Schema(self._schema.additionalProperties)
        self._push_schema(schema, ".additionalProperties")

    def _push_array_schema(self):
        schema = Schema(self._schema.items)
        self._push_schema(schema, ".items")

    def _push_array_item_object(self, index):
        self._push_object(self._object[index], "[%d]" % index)

    def _push_property_object(self, prop):
        self._push_object(self._object[prop], "." + prop)

    def _report_unsupported(self):
        schema = self._schema
        if schema.contentEncoding is not None:
            raise NotImplementedError("contentEncoding is not supported")
        if schema.divisibleBy != 1:
            raise NotImplementedError("divisibleBy is not supported")
        if schema.disallow is not None:
            raise NotImplementedError("disallow is not supported")

    def _validate_type(self):
        schema = self._schema
        json_type = schema.type
        if json_type == "any":
            return
        obj = self._object
        if json_type == "boolean":
            # Bool is special cased because in python there is no
            # way to test for isinstance(something, bool) that would
            # not catch isinstance(1, bool) :/
            if obj is not True and obj is not False:
                self._report_error(
                    "{obj!r} does not match type {type!r}".format(
                        obj=obj, type=json_type),
                    "Object has incorrect type (expected boolean)",
                    schema_suffix=".type")
        elif isinstance(json_type, dict):
            # Nested type check. This is pretty odd case. Here we
            # don't change our object stack (it's the same object).
            self._push_schema(Schema(json_type), ".type")
            self._validate()
            self._pop_schema()
        elif isinstance(json_type, list):
            # Alternative type check, here we may match _any_ of the types
            # in the list to be considered valid.
            json_type_list = json_type
            if json_type == []:
                return
            for index, json_type in enumerate(json_type_list):
                # Aww, ugly. The level of packaging around Schema is annoying
                self._push_schema(
                    Schema({'type': json_type}),
                    ".type.%d" % index)
                try:
                    self._validate()
                except ValidationError:
                    # Ignore errors, we just want one thing to match
                    pass
                else:
                    # We've got a match - break the loop
                    break
                finally:
                    # Pop the schema regardless of match/mismatch
                    self._pop_schema()
            else:
                # We were not interupted (no break) so we did not match
                self._report_error(
                    "{obj!r} does not match any of the types in {type!r}".format(
                        obj=obj, type=json_type_list),
                    "Object has incorrect type (multiple types possible)",
                    schema_suffix=".type")
        else:
            # Simple type check
            if not isinstance(obj, self.JSON_TYPE_MAP[json_type]):
                self._report_error(
                    "{obj!r} does not match type {type!r}".format(
                        obj=obj, type=json_type),
                    "Object has incorrect type (expected {type})".format(
                        type=json_type),
                    schema_suffix=".type")

    def _validate_pattern(self):
        ptn = self._schema.pattern
        obj = self._object

        if ptn is None:
            return
        if not isinstance(obj, basestring):
            return
        if re.match(ptn, obj):
            return

        self._report_error(
            "{obj!r} does not match pattern {ptn!r}".format(
                obj=obj,ptn=ptn),
            "Object does not match pattern (expected {ptn})".format(
                ptn=ptn),
            schema_suffix=".pattern"
        )

    def _validate_format(self):
        fmt = self._schema.format
        obj = self._object
        if fmt is None:
            return
        if fmt == 'date-time':
            try:
                DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
                datetime.datetime.strptime(obj, DATE_TIME_FORMAT)
            except ValueError:
                self._report_error(
                    "{obj!r} is not a string representing JSON date-time".format(
                        obj=obj),
                    "Object is not a string representing JSON date-time",
                    schema_suffix=".format")
        elif fmt == 'regex':
            try:
                re.compile(obj)
            except:
                self._report_error(
                    "{obj!r} is not a string representing a regex".format(
                        obj=obj),
                    "Object is not a string representing a regex",
                    schema_suffix=".format")
        else:
            raise NotImplementedError("format {0!r} is not supported".format(fmt))

    def _validate_properties(self):
        obj = self._object
        schema = self._schema
        assert isinstance(obj, dict)
        for prop in schema.properties.keys():
            self._push_property_schema(prop)
            if prop in obj:
                self._push_property_object(prop)
                self._validate()
                self._pop_object()
            else:
                if not self._schema.optional:
                    self._report_error(
                        "{obj!r} does not have property {prop!r}".format(
                            obj=obj, prop=prop),
                        "Object lacks property {prop!r}".format(
                            prop=prop),
                        schema_suffix=".optional")
            self._pop_schema()

    def _validate_additional_properties(self):
        obj = self._object
        assert isinstance(obj, dict)
        if self._schema.additionalProperties is False:
            # Additional properties are disallowed
            # Report exception for each unknown property
            for prop in obj.keys():
                if prop not in self._schema.properties:
                    self._report_error(
                        "{obj!r} has unknown property {prop!r} and"
                        " additionalProperties is false".format(
                            obj=obj, prop=prop),
                        "Object has unknown property {prop!r} but"
                        " additional properties are disallowed".format(
                            prop=prop),
                        schema_suffix=".additionalProperties")
        else:
            # Check each property against this object
            self._push_additional_property_schema()
            for prop in obj.keys():
                self._push_property_object(prop)
                self._validate()
                self._pop_object()
            self._pop_schema()

    def _validate_enum(self):
        obj = self._object
        schema = self._schema
        if schema.enum is not None:
            for allowed_value in schema.enum:
                if obj == allowed_value:
                    break
            else:
                self._report_error(
                    "{obj!r} does not match any value in enumeration"
                    " {enum!r}".format(obj=obj, enum=schema.enum),
                    "Object does not match any value in enumeration",
                    schema_suffix=".enum")

    def _validate_length(self):
        obj = self._object
        schema = self._schema
        if schema.minLength is not None:
            if len(obj) < schema.minLength:
                self._report_error(
                    "{obj!r} does not meet the minimum length"
                    " {minLength!r}".format(obj=obj, minLength=schema.minLength),
                    "Object does not meet the minimum length",
                    schema_suffix=".minLength")
        if schema.maxLength is not None:
            if len(obj) > schema.maxLength:
                self._report_error(
                    "{obj!r} exceeds the maximum length"
                    " {maxLength!r}".format(obj=obj, maxLength=schema.maxLength),
                    "Object exceeds the maximum length",
                    schema_suffix=".maxLength")

    def _validate_range(self):
        obj = self._object
        schema = self._schema
        if schema.minimum is not None:
            if obj < schema.minimum or (obj == schema.minimum and not schema.minimumCanEqual):
                self._report_error(
                    "{obj!r} is less than the minimum"
                    " {minimum!r}".format(obj=obj, minimum=schema.minimum),
                    "Object is less than the minimum",
                    schema_suffix=".minimum")
        if schema.maximum is not None:
            if obj > schema.maximum or (obj == schema.maximum and not schema.maximumCanEqual):
                self._report_error(
                    "{obj!r} is greater than the maximum"
                    " {maximum!r}".format(obj=obj, maximum=schema.maximum),
                    "Object is greater than the maximum",
                    schema_suffix=".maximum")

    def _validate_items(self):
        obj = self._object
        schema = self._schema
        assert isinstance(obj, list)
        items_schema_json = schema.items
        if items_schema_json == {}:
            # default value, don't do anything
            return
        if isinstance(obj, list) and schema.uniqueItems is True and len(set(obj)) != len(obj):
            # If we want a list of unique items and the length of unique
            # elements is different from the length of the full list
            # then validation fails.
            # This implementation isn't strictly compatible with the specs, because
            # we are not checking unique dicts.
            self._report_error(
                "Repeated items found in {obj!r}".format(obj=obj),
                "Repeated items found in array",
                schema_suffix=".items")
        if schema.minItems:
            if len(obj) < schema.minItems:
                self._report_error(
                    "{obj!r} has fewer than the minimum number of items"
                    " {minItems!r}".format(obj=obj, minimum=schema.minItems),
                    "Object has fewer than the minimum number of items",
                    schema_suffix=".minItems")
        if schema.maxItems is not None:
            if len(obj) > schema.maxItems:
                self._report_error(
                    "{obj!r} has more than the maximum number of items"
                    " {maxItems!r}".format(obj=obj, minimum=schema.maxItems),
                    "Object has more than the maximum number of items",
                    schema_suffix=".maxItems")
        if isinstance(items_schema_json, dict):
            self._push_array_schema()
            for index, item in enumerate(obj):
                self._push_array_item_object(index)
                self._validate()
                self._pop_object()
            self._pop_schema()
        elif isinstance(items_schema_json, list):
            if len(obj) < len(items_schema_json):
                # If our data array is shorter than the schema then
                # validation fails. Longer arrays are okay (during this
                # step) as they are validated based on
                # additionalProperties schema
                self._report_error(
                    "{obj!r} is shorter than array schema {schema!r}".
                    format(obj=obj, schema=items_schema_json),
                    "Object array is shorter than schema array",
                    schema_suffix=".items")
            if len(obj) != len(items_schema_json) and schema.additionalProperties is False:
                # If our array is not exactly the same size as the
                # schema and additional properties are disallowed then
                # validation fails
                self._report_error(
                    "{obj!r} is not of the same length as array schema"
                    " {schema!r} and additionalProperties is"
                    " false".format(obj=obj, schema=items_schema_json),
                    "Object array is not of the same length as schema array",
                    schema_suffix=".items")
            # Validate each array element using schema for the
            # corresponding array index, fill missing values (since
            # there may be more items in our array than in the schema)
            # with additionalProperties which by now is not False
            for index, (item, item_schema_json) in enumerate(
                zip_longest(
                    obj, items_schema_json,
                    fillvalue=schema.additionalProperties)):
                item_schema = Schema(item_schema_json)
                if index < len(items_schema_json):
                    self._push_schema(item_schema, "items[%d]" % index)
                else:
                    self._push_schema(item_schema, ".additionalProperties")
                self._push_array_item_object(index)
                self._validate()
                self._pop_schema()
                self._pop_object()

    def _validate_requires(self):
        obj = self._object
        schema = self._schema
        requires_json = schema.requires
        if requires_json == {}:
            # default value, don't do anything
            return
        # Find our enclosing object in the object stack
        if len(self._object_stack) < 2:
            self._report_error(
                "{obj!r} requires that enclosing object matches"
                " schema {schema!r} but there is no enclosing"
                " object".format(obj=obj, schema=requires_json),
                "Object has no enclosing object that matches schema",
                schema_suffix=".requires")
        # Note: Parent object can be None, (e.g. a null property)
        parent_obj = self._object_stack[-2][0]
        if isinstance(requires_json, basestring):
            # This is a simple property test
            if (not isinstance(parent_obj, dict)
                or requires_json not in parent_obj):
                self._report_error(
                    "{obj!r} requires presence of property {requires!r}"
                    " in the same object".format(
                        obj=obj, requires=requires_json),
                    "Enclosing object does not have property"
                    " {prop!r}".format(prop=requires_json),
                    schema_suffix=".requires")
        elif isinstance(requires_json, dict):
            # Requires designates a whole schema, the enclosing object
            # must match against that schema.
            # Here we resort to a small hack. Proper implementation
            # would require us to validate the parent object from its
            # own context (own list of parent objects). Since doing that
            # and restoring the state would be very complicated we just
            # instantiate a new validator with a subset of our current
            # history here.
            sub_validator = Validator()
            sub_validator._object_stack = self._object_stack[:-1]
            sub_validator._schema_stack = self._schema_stack[:]
            sub_validator._push_schema(
                Schema(requires_json), ".requires")
            sub_validator._validate()
