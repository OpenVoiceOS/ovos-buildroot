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

"""Error classes used by this package."""


class SchemaError(ValueError):
    """Exception raised when there is a problem with the schema itself."""


class ValidationError(ValueError):
    """
    Exception raised on mismatch between the validated object and the schema.

    .. attribute:: message

        Old and verbose message that contains less helpful message and lots of
        JSON data (deprecated).

    .. attribute:: new_message

        Short and concise message about the problem.

    .. attribute:: object_expr

        A JavaScript expression that evaluates to the object that failed to
        validate. The expression always starts with a root object called
        ``'object'``.

    .. attribute:: schema_expr

        A JavaScript expression that evaluates to the schema that was checked
        at the time validation failed. The expression always starts with a root
        object called ``'schema'``.
    """

    def __init__(self, message, new_message=None,
                 object_expr=None, schema_expr=None):
        self.message = message
        self.new_message = new_message
        self.object_expr = object_expr
        self.schema_expr = schema_expr

    def __str__(self):
        return ("ValidationError: {0} "
                "object_expr={1!r}, "
                "schema_expr={2!r})").format(
                    self.new_message, self.object_expr,
                    self.schema_expr)
