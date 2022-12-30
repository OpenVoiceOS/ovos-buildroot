# SPDX-FileCopyrightText: Copyright (c) 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""
`circuitpython_typing.led`
================================================================================

Type annotation definitions for LEDs.

* Author(s): Alec Delaney
"""

# Protocol was introduced in Python 3.8, TypeAlias in 3.10
from typing import Union, Tuple
from typing_extensions import Protocol, TypeAlias

ColorBasedColorUnion: TypeAlias = Union[int, Tuple[int, int, int]]
FillBasedColorUnion: TypeAlias = Union[ColorBasedColorUnion, Tuple[int, int, int, int]]


class ColorBasedLED(Protocol):
    """Protocol for LEDs using the :meth:`color` method"""

    def color(self, value: ColorBasedColorUnion) -> None:
        """Sets the color of the LED"""


class FillBasedLED(Protocol):
    """Protocol for LEDs using the :meth:`fill` method"""

    def fill(self, color: FillBasedColorUnion) -> None:
        """Sets the color of the LED"""
