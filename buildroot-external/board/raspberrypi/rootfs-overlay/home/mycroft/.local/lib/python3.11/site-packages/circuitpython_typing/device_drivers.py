# SPDX-FileCopyrightText: Copyright (c) 2022 Alec Delaney
# SPDX-License-Identifier: MIT
"""
`circuitpython_typing.device_drivers`
================================================================================

Type annotation definitions for device drivers. Used for `adafruit_register`.

* Author(s): Alec Delaney
"""

from adafruit_bus_device.i2c_device import I2CDevice
from typing_extensions import Protocol  # Safety import for Python 3.7


# pylint: disable=too-few-public-methods
class I2CDeviceDriver(Protocol):
    """Describes classes that are drivers utilizing `I2CDevice`"""

    i2c_device: I2CDevice
