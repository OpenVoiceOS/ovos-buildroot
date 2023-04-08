# SPDX-FileCopyrightText: Copyright (c) 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""
`circuitpython_typing.io`
================================================================================

Type annotation definitions for IO-related objects

* Author(s): Alec Delaney
"""

# Protocol was introduced in Python 3.8.
from typing_extensions import Protocol


class ROValueIO(Protocol):
    """Hardware objects, like `analogio.AnalogIn`, that have read-only
    ``value`` properties/attributes.
    """

    @property
    def value(self) -> float:
        """Value property, that may return an `int` or `float` depending
        on the specifics of the class.
        """


class ValueIO(Protocol):
    """Hardware objects, like `analogio.AnalogOut`, that have read and
    write ``value`` properties/attributes.
    """

    @property
    def value(self) -> float:
        """Value property, that may return an `int` or `float` depending
        on the specifics of the class.
        """

    # pylint: disable=no-self-use,unused-argument
    @value.setter
    def value(self, input_value: float, /):
        ...
