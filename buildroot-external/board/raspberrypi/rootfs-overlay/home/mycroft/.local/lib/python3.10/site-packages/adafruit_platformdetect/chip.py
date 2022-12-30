# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_platformdetect.chip`
================================================================================

Attempt detection of current chip / CPU

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Linux and Python 3.7 or Higher

"""


import os
import sys

try:
    from typing import Optional
except ImportError:
    pass

from adafruit_platformdetect.constants import chips


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_PlatformDetect.git"


class Chip:
    """Attempt detection of current chip / CPU."""

    def __init__(self, detector) -> None:
        self.detector = detector
        self._chip_id = None

    @property
    def id(
        self,
    ) -> Optional[
        str
    ]:  # pylint: disable=invalid-name,too-many-branches,too-many-return-statements
        """Return a unique id for the detected chip, if any."""
        # There are some times we want to trick the platform detection
        # say if a raspberry pi doesn't have the right ID, or for testing

        # Caching
        if self._chip_id:
            return self._chip_id

        if getattr(os, "environ", None) is not None:
            try:
                return os.environ["BLINKA_FORCECHIP"]
            except KeyError:  # no forced chip, continue with testing!
                pass

            # Special cases controlled by environment var
            if os.environ.get("BLINKA_FT232H"):
                from pyftdi.usbtools import UsbTools

                # look for it based on PID/VID
                count = len(UsbTools.find_all([(0x0403, 0x6014)]))
                if count == 0:
                    raise RuntimeError(
                        "BLINKA_FT232H environment variable "
                        + "set, but no FT232H device found"
                    )
                self._chip_id = chips.FT232H
                return self._chip_id
            if os.environ.get("BLINKA_FT2232H"):
                from pyftdi.usbtools import UsbTools

                # look for it based on PID/VID
                count = len(UsbTools.find_all([(0x0403, 0x6010)]))
                if count == 0:
                    raise RuntimeError(
                        "BLINKA_FT2232H environment variable "
                        + "set, but no FT2232H device found"
                    )
                self._chip_id = chips.FT2232H
                return self._chip_id
            if os.environ.get("BLINKA_MCP2221"):
                import hid

                # look for it based on PID/VID
                for dev in hid.enumerate():
                    if dev["vendor_id"] == 0x04D8 and dev["product_id"] == 0x00DD:
                        self._chip_id = chips.MCP2221
                        return self._chip_id
                raise RuntimeError(
                    "BLINKA_MCP2221 environment variable "
                    + "set, but no MCP2221 device found"
                )
            if os.environ.get("BLINKA_U2IF"):
                import hid

                # look for it based on PID/VID
                for dev in hid.enumerate():
                    vendor = dev["vendor_id"]
                    product = dev["product_id"]
                    # NOTE: If any products are added here, they need added
                    # to _rp2040_u2if_id() in board.py as well.
                    if (
                        # Raspberry Pi Pico
                        vendor == 0xCAFE
                        and product == 0x4005
                    ) or (
                        # Feather RP2040
                        # Itsy Bitsy RP2040
                        # QT Py RP2040
                        # QT2040 Trinkey
                        # MacroPad RP2040
                        vendor == 0x239A
                        and product in (0x00F1, 0x00FD, 0x00F7, 0x0109, 0x0107)
                    ):
                        self._chip_id = chips.RP2040_U2IF
                        return self._chip_id
                raise RuntimeError(
                    "BLINKA_U2IF environment variable "
                    + "set, but no compatible device found"
                )
            if os.environ.get("BLINKA_GREATFET"):
                import usb

                if usb.core.find(idVendor=0x1D50, idProduct=0x60E6) is not None:
                    self._chip_id = chips.LPC4330
                    return self._chip_id
                raise RuntimeError(
                    "BLINKA_GREATFET environment variable "
                    + "set, but no GreatFET device found"
                )
            if os.environ.get("BLINKA_NOVA"):
                self._chip_id = chips.BINHO
                return self._chip_id

        platform = sys.platform
        if platform in ("linux", "linux2"):
            self._chip_id = self._linux_id()
            return self._chip_id
        if platform == "esp8266":
            self._chip_id = chips.ESP8266
            return self._chip_id
        if platform == "samd21":
            self._chip_id = chips.SAMD21
            return self._chip_id
        if platform == "pyboard":
            self._chip_id = chips.STM32F405
            return self._chip_id
        if platform == "rp2":
            self._chip_id = chips.RP2040
            return self._chip_id
        # nothing found!
        return None

    # pylint: enable=invalid-name

    def _linux_id(self) -> Optional[str]:
        # pylint: disable=too-many-branches,too-many-statements
        # pylint: disable=too-many-return-statements
        """Attempt to detect the CPU on a computer running the Linux kernel."""
        if self.detector.check_dt_compatible_value("ti,am654"):
            return chips.AM65XX

        if self.detector.check_dt_compatible_value("ti,am652"):
            return chips.AM65XX

        if self.detector.check_dt_compatible_value("sun4i-a10"):
            return chips.A10

        if self.detector.check_dt_compatible_value("sun7i-a20"):
            return chips.A20

        if self.detector.check_dt_compatible_value("amlogic,g12a"):
            return chips.S905Y2
        if self.detector.check_dt_compatible_value("amlogic, g12a"):
            return chips.S905X3

        if self.detector.check_dt_compatible_value("sun8i-h3"):
            return chips.H3

        if self.detector.check_dt_compatible_value("qcom,apq8016"):
            return chips.APQ8016

        if self.detector.check_dt_compatible_value("fu500"):
            return chips.HFU540

        if self.detector.check_dt_compatible_value("sun20iw1p1"):
            return chips.C906

        # Older Builds
        if self.detector.check_dt_compatible_value("sifive"):
            return chips.JH71x0

        # Newer Builds
        if self.detector.check_dt_compatible_value("jh7100"):
            return chips.JH71x0

        if self.detector.check_dt_compatible_value("sun8i-a33"):
            return chips.A33

        if self.detector.check_dt_compatible_value("rockchip,rk3308"):
            return chips.RK3308

        if self.detector.check_dt_compatible_value("radxa,rock-4c-plus"):
            return chips.RK3399_T

        if self.detector.check_dt_compatible_value("rockchip,rk3399"):
            return chips.RK3399

        if self.detector.check_dt_compatible_value("rockchip,rk3288"):
            return chips.RK3288

        if self.detector.check_dt_compatible_value("rockchip,rk3328"):
            return chips.RK3328

        if self.detector.check_dt_compatible_value("rockchip,rk3566"):
            return chips.RK3566

        if self.detector.check_dt_compatible_value("rockchip,rk3568"):
            return chips.RK3568

        if self.detector.check_dt_compatible_value("rockchip,rk3568b2"):
            return chips.RK3568B2

        if self.detector.check_dt_compatible_value("rockchip,rk3588"):
            return chips.RK3588

        if self.detector.check_dt_compatible_value("amlogic,a311d"):
            return chips.A311D

        if self.detector.check_dt_compatible_value("st,stm32mp157"):
            return chips.STM32MP157

        if self.detector.check_dt_compatible_value("st,stm32mp153"):
            return chips.STM32MP157DAA1

        if self.detector.check_dt_compatible_value("sun50i-a64"):
            return chips.A64

        if self.detector.check_dt_compatible_value("sun50i-h5"):
            return chips.H5

        if self.detector.check_dt_compatible_value("sun50i-h616"):
            return chips.H616

        if self.detector.check_dt_compatible_value("sun50iw9"):
            return chips.H616

        if self.detector.check_dt_compatible_value("sun50i-h6"):
            return chips.H6

        if self.detector.check_dt_compatible_value("mediatek,mt8167"):
            return chips.MT8167

        if self.detector.check_dt_compatible_value("imx6ull"):
            return chips.IMX6ULL

        if self.detector.check_dt_compatible_value("ti,j721e"):
            return chips.TDA4VM

        if self.detector.check_dt_compatible_value("sun20i-d1"):
            return chips.D1_RISCV

        if self.detector.check_dt_compatible_value("libretech,aml-s905x-cc"):
            return chips.S905X

        linux_id = None
        hardware = self.detector.get_cpuinfo_field("Hardware")

        if hardware is None:
            vendor_id = self.detector.get_cpuinfo_field("vendor_id")
            if vendor_id == "AuthenticAMD":
                model_name = self.detector.get_cpuinfo_field("model name").upper()
                if "RYZEN EMBEDDED V1202B" in model_name:
                    linux_id = chips.RYZEN_V1202B
                if "RYZEN EMBEDDED V1605B" in model_name:
                    linux_id = chips.RYZEN_V1605B
                else:
                    linux_id = chips.GENERIC_X86
            ##            print("linux_id = ", linux_id)
            elif vendor_id == "GenuineIntel":
                model_name = self.detector.get_cpuinfo_field("model name").upper()
                ##                print('model_name =', model_name)
                if "N3710" in model_name:
                    linux_id = chips.PENTIUM_N3710
                elif "X5-Z8350" in model_name:
                    linux_id = chips.ATOM_X5_Z8350
                elif "J4105" in model_name:
                    linux_id = chips.ATOM_J4105
                else:
                    linux_id = chips.GENERIC_X86
            ##            print("linux_id = ", linux_id)

            compatible = self.detector.get_device_compatible()
            if compatible and "tegra" in compatible:
                compats = compatible.split("\x00")
                if "nvidia,tegra210" in compats:
                    linux_id = chips.T210
                elif "nvidia,tegra186" in compats:
                    linux_id = chips.T186
                elif "nvidia,tegra194" in compats:
                    linux_id = chips.T194
                elif "nvidia,tegra234" in compats:
                    linux_id = chips.T234
            if compatible and "imx8m" in compatible:
                linux_id = chips.IMX8MX
            if compatible and "odroid-c2" in compatible:
                linux_id = chips.S905
            if compatible and "amlogic" in compatible:
                compatible_list = (
                    compatible.replace("\x00", ",").replace(" ", "").split(",")
                )
                if "g12a" in compatible_list:
                    # 'sm1' is correct for S905X3, but some kernels use 'g12a'
                    return chips.S905X3
                if "g12b" in compatible_list:
                    return chips.S922X
                if "sm1" in compatible_list:
                    return chips.S905X3
                if "vim3amlogic" in compatible_list:
                    return chips.A311D
            if compatible and "sun50i-a64" in compatible:
                linux_id = chips.A64
            if compatible and "sun50i-h6" in compatible:
                linux_id = chips.H6
            if compatible and "sun50i-h5" in compatible:
                linux_id = chips.H5
            if compatible and "odroid-xu4" in compatible:
                linux_id = chips.EXYNOS5422
            cpu_model = self.detector.get_cpuinfo_field("cpu model")

            if cpu_model is not None:
                if "MIPS 24Kc" in cpu_model:
                    linux_id = chips.MIPS24KC
                elif "MIPS 24KEc" in cpu_model:
                    linux_id = chips.MIPS24KEC

            # we still haven't identified the hardware, so
            # convert it to a list and let the remaining
            # conditions attempt.
            if not linux_id:
                hardware = [
                    entry.replace("\x00", "") for entry in compatible.split(",")
                ]

        if not linux_id:
            if "AM33XX" in hardware:
                linux_id = chips.AM33XX
            elif "DRA74X" in hardware:
                linux_id = chips.DRA74X
            elif "sun4i" in hardware:
                linux_id = chips.A10
            elif "sun7i" in hardware:
                linux_id = chips.A20
            elif "sun8i" in hardware:
                linux_id = chips.SUN8I
            elif "ODROIDC" in hardware:
                linux_id = chips.S805
            elif "ODROID-C2" in hardware:
                linux_id = chips.S905
            elif "ODROID-N2" in hardware:
                linux_id = chips.S922X
            elif "ODROID-C4" in hardware:
                linux_id = chips.S905X3
            elif "ODROID-XU4" in hardware:
                linux_id = chips.EXYNOS5422
            elif "KHADAS-VIM3" in hardware:
                linux_id = chips.A311D
            elif "SAMA5" in hardware:
                linux_id = chips.SAMA5
            elif "Pinebook" in hardware:
                linux_id = chips.A64
            elif "ASUS_TINKER_BOARD" in hardware:
                linux_id = chips.RK3288
            elif "Xilinx Zynq" in hardware:
                compatible = self.detector.get_device_compatible()
                if compatible and "xlnx,zynq-7000" in compatible:
                    linux_id = chips.ZYNQ7000
            else:
                if isinstance(hardware, str):
                    if hardware.upper() in chips.BCM_RANGE:
                        linux_id = chips.BCM2XXX
                elif isinstance(hardware, list):
                    if {model.upper() for model in hardware} & chips.BCM_RANGE:
                        linux_id = chips.BCM2XXX

        return linux_id

    def __getattr__(self, attr: str) -> bool:
        """
        Detect whether the given attribute is the currently-detected chip.  See
        list of constants at the top of this module for available options.
        """
        if self.id == attr:
            return True
        return False
