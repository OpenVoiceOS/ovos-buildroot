# SPDX-FileCopyrightText: 2014-2018 Tony DiCola, Limor Fried, Brennen Bearnes
#
# SPDX-License-Identifier: MIT

"""
Attempt to detect the current platform.
"""
import os
import re
import sys

try:
    from typing import Optional
except ImportError:
    pass

from adafruit_platformdetect.board import Board
from adafruit_platformdetect.chip import Chip

# Needed to find libs (like libusb) installed by homebrew on Apple Silicon
if sys.platform == "darwin":
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib/"

# Various methods here may retain state in future, so tell pylint not to worry
# that they don't use self right now:
# pylint: disable=no-self-use
class Detector:
    """Wrap various platform detection functions."""

    def __init__(self) -> None:
        self.board = Board(self)
        self.chip = Chip(self)

    def get_cpuinfo_field(self, field: str) -> Optional[str]:
        """
        Search /proc/cpuinfo for a field and return its value, if found,
        otherwise None.
        """
        # Match a line like 'Hardware   : BCM2709':
        pattern = r"^" + field + r"\s+:\s+(.*)$"

        with open("/proc/cpuinfo", "r", encoding="utf-8") as infile:
            cpuinfo = infile.read().split("\n")
        for line in cpuinfo:
            match = re.search(pattern, line, flags=re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def check_dt_compatible_value(self, value: str) -> bool:
        """
        Search /proc/device-tree/compatible for a value and return True, if found,
        otherwise False.
        """
        # Match a value like 'qcom,apq8016-sbc':
        dt_compatible = self.get_device_compatible()
        if dt_compatible and value in dt_compatible:
            return True

        return False

    def get_armbian_release_field(self, field: str) -> Optional[str]:
        """
        Search /etc/armbian-release, if it exists, for a field and return its
        value, if found, otherwise None.
        """
        field_value = None

        pattern = r"^" + field + r"=(.*)"
        try:
            with open("/etc/armbian-release", "r", encoding="utf-8") as release_file:
                armbian = release_file.read().split("\n")
                for line in armbian:
                    match = re.search(pattern, line)
                    if match:
                        field_value = match.group(1)
        except FileNotFoundError:
            pass

        return field_value

    def get_device_model(self) -> Optional[str]:
        """
        Search /proc/device-tree/model for the device model and return its value, if found,
        otherwise None.
        """
        try:
            with open("/proc/device-tree/model", "r", encoding="utf-8") as model_file:
                return model_file.read()
        except FileNotFoundError:
            pass
        return None

    def get_device_compatible(self) -> Optional[str]:
        """
        Search /proc/device-tree/compatible for the compatible chip name.
        """
        try:
            with open(
                "/proc/device-tree/compatible", "r", encoding="utf-8"
            ) as model_file:
                return model_file.read()
        except FileNotFoundError:
            pass
        return None

    def check_board_asset_tag_value(self) -> Optional[str]:
        """
        Search /sys/devices/virtual/dmi/id for the device model and return its value, if found,
        otherwise None.
        """
        try:
            with open(
                "/sys/devices/virtual/dmi/id/board_asset_tag", "r", encoding="utf-8"
            ) as tag_file:
                return tag_file.read().strip()
        except FileNotFoundError:
            pass
        return None

    def check_board_name_value(self) -> Optional[str]:
        """
        Search /sys/devices/virtual/dmi/id for the board name and return its value, if found,
        otherwise None. Debian/ubuntu based
        """
        try:
            with open(
                "/sys/devices/virtual/dmi/id/board_name", "r", encoding="utf-8"
            ) as board_name_file:
                return board_name_file.read().strip()
        except FileNotFoundError:
            pass
        return None
