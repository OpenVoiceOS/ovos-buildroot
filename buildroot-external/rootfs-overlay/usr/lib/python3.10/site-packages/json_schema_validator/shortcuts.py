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

"""One liners that make the code shorter."""

try:
    import simplejson as json
except ImportError:
    import json

from json_schema_validator.schema import Schema
from json_schema_validator.validator import Validator

_default_deserializer = json.loads


def validate(schema_text, data_text, deserializer=_default_deserializer):
    """
    Validate specified JSON text with specified schema.

    Both arguments are converted to JSON objects with :func:`simplejson.loads`,
    if present, or :func:`json.loads`.

    :param schema_text:
        Text of the JSON schema to check against
    :type schema_text:
        :class:`str`
    :param data_text:
        Text of the JSON object to check
    :type data_text:
        :class:`str`
    :param deserializer:
        Function to convert the schema and data to JSON objects
    :type deserializer:
        :class:`callable`
    :returns:
        Same as :meth:`json_schema_validator.validator.Validator.validate`
    :raises:
        Whatever may be raised by simplejson (in particular
        :class:`simplejson.decoder.JSONDecoderError`, a subclass of
        :class:`ValueError`) or json
    :raises:
        Whatever may be raised by
        :meth:`json_schema_validator.validator.Validator.validate`. In particular
        :class:`json_schema_validator.errors.ValidationError` and
        :class:`json_schema_validator.errors.SchemaError`
    """
    schema = Schema(deserializer(schema_text))
    data = deserializer(data_text)
    return Validator.validate(schema, data)
