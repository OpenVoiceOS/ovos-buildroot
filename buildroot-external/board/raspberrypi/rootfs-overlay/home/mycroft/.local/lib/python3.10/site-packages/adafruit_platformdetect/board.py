# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT


"""
`adafruit_platformdetect.board`
================================================================================

Detect boards

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Linux and Python 3.7 or Higher

"""

import os
import re

try:
    from typing import Optional
except ImportError:
    pass

from adafruit_platformdetect.constants import boards, chips


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_PlatformDetect.git"


class Board:
    """Attempt to detect specific boards."""

    def __init__(self, detector) -> None:
        self.detector = detector
        self._board_id = None

    # pylint: disable=invalid-name, protected-access, too-many-return-statements
    @property
    def id(self) -> Optional[str]:
        """Return a unique id for the detected board, if any."""
        # There are some times we want to trick the platform detection
        # say if a raspberry pi doesn't have the right ID, or for testing

        # Caching
        if self._board_id:
            return self._board_id

        try:
            return os.environ["BLINKA_FORCEBOARD"]
        except (AttributeError, KeyError):  # no forced board, continue with testing!
            pass

        chip_id = self.detector.chip.id
        board_id = None

        if chip_id == chips.H3:
            board_id = self._armbian_id() or self._allwinner_variants_id()
        elif chip_id == chips.BCM2XXX:
            board_id = self._pi_id()
        elif chip_id == chips.AM33XX:
            board_id = self._beaglebone_id()
        elif chip_id == chips.AM65XX:
            board_id = self._siemens_simatic_iot2000_id()
        elif chip_id == chips.DRA74X:
            board_id = self._bbai_id()
        elif chip_id == chips.SUN4I:
            board_id = self._armbian_id()
        elif chip_id == chips.SUN7I:
            board_id = self._armbian_id()
        elif chip_id == chips.SUN8I:
            board_id = self._armbian_id() or self._allwinner_variants_id()
        elif chip_id == chips.SAMA5:
            board_id = self._sama5_id()
        elif chip_id == chips.IMX8MX:
            board_id = self._imx8mx_id()
        elif chip_id == chips.IMX6ULL:
            board_id = self._imx6ull_id()
        elif chip_id == chips.S905Y2:
            board_id = boards.RADXA_ZERO
        elif chip_id == chips.ESP8266:
            board_id = boards.FEATHER_HUZZAH
        elif chip_id == chips.SAMD21:
            board_id = boards.FEATHER_M0_EXPRESS
        elif chip_id == chips.STM32F405:
            board_id = boards.PYBOARD
        elif chip_id == chips.RP2040:
            board_id = boards.RASPBERRY_PI_PICO
        elif chip_id == chips.S805:
            board_id = boards.ODROID_C1
        elif chip_id == chips.RK3568B2:
            board_id = boards.ODROID_M1
        elif chip_id == chips.S905:
            board_id = boards.ODROID_C2
        elif chip_id == chips.S905X3:
            board_id = self._s905x3_id()
        elif chip_id == chips.S922X:
            board_id = boards.ODROID_N2
        elif chip_id == chips.A311D:
            board_id = boards.KHADAS_VIM3
        elif chip_id == chips.EXYNOS5422:
            board_id = boards.ODROID_XU4
        elif chip_id == chips.FT232H:
            board_id = boards.FTDI_FT232H
        elif chip_id == chips.FT2232H:
            board_id = boards.FTDI_FT2232H
        elif chip_id == chips.APQ8016:
            board_id = boards.DRAGONBOARD_410C
        elif chip_id in (chips.T210, chips.T186, chips.T194, chips.T234):
            board_id = self._tegra_id()
        elif chip_id == chips.HFU540:
            board_id = self._sifive_id()
        elif chip_id == chips.C906:
            board_id = self._allwinner_id()
        elif chip_id == chips.JH71x0:
            board_id = self._beaglebone_id()
        elif chip_id == chips.MCP2221:
            board_id = boards.MICROCHIP_MCP2221
        elif chip_id == chips.BINHO:
            board_id = boards.BINHO_NOVA
        elif chip_id == chips.LPC4330:
            board_id = boards.GREATFET_ONE
        elif chip_id == chips.MIPS24KC:
            board_id = boards.ONION_OMEGA
        elif chip_id == chips.MIPS24KEC:
            board_id = boards.ONION_OMEGA2
        elif chip_id == chips.ZYNQ7000:
            board_id = self._pynq_id()
        elif chip_id == chips.A10:
            board_id = self._armbian_id()
        elif chip_id == chips.A20:
            board_id = self._armbian_id()
        elif chip_id == chips.A64:
            board_id = self._pine64_id()
        elif chip_id == chips.H6:
            board_id = self._pine64_id() or self._armbian_id()
        elif chip_id == chips.H5:
            board_id = self._armbian_id() or self._allwinner_variants_id()
        elif chip_id == chips.H616:
            board_id = self._armbian_id() or self._allwinner_variants_id()
        elif chip_id == chips.A33:
            board_id = self._clockwork_pi_id()
        elif chip_id == chips.RK3308:
            board_id = self._rock_pi_id()
        elif chip_id == chips.RK3399:
            board_id = self._rock_pi_id() or self._armbian_id()
        elif chip_id == chips.RK3399_T:
            board_id = self._rock_pi_id() or self._armbian_id()
        elif chip_id == chips.ATOM_X5_Z8350:
            board_id = self._rock_pi_id()
        elif chip_id == chips.ATOM_J4105:
            board_id = self._j4105_id()
        elif chip_id == chips.RK3288:
            board_id = self._asus_tinker_board_id()
        elif chip_id == chips.RK3328:
            board_id = self._rock_pi_id()
        elif chip_id == chips.RK3566:
            board_id = self._rk3566_id()
        elif chip_id == chips.RK3568:
            board_id = self._rk3568_id()
        elif chip_id == chips.RK3588:
            board_id = self._rock_pi_id()
        elif chip_id == chips.RYZEN_V1605B:
            board_id = self._udoo_id()
        elif chip_id == chips.PENTIUM_N3710:
            board_id = self._udoo_id()
        elif chip_id == chips.STM32MP157:
            board_id = self._stm32mp1_id()
        elif chip_id == chips.STM32MP157DAA1:
            board_id = self._stm32mp1_id()
        elif chip_id == chips.MT8167:
            board_id = boards.CORAL_EDGE_TPU_DEV_MINI
        elif chip_id == chips.RP2040_U2IF:
            board_id = self._rp2040_u2if_id()
        elif chip_id == chips.GENERIC_X86:
            board_id = boards.GENERIC_LINUX_PC
        elif chip_id == chips.TDA4VM:
            board_id = self._tisk_id()
        elif chip_id == chips.D1_RISCV:
            board_id = self._armbian_id()
        elif chip_id == chips.S905X:
            board_id = boards.AML_S905X_CC
        self._board_id = board_id
        return board_id

    # pylint: enable=invalid-name

    def _pi_id(self) -> Optional[str]:
        """Try to detect id of a Raspberry Pi."""
        # Check for Pi boards:
        pi_rev_code = self._pi_rev_code()
        if pi_rev_code:
            for model, codes in boards._PI_REV_CODES.items():
                if pi_rev_code in codes:
                    return model

        # We may be on a non-Raspbian OS, so try to lazily determine
        # the version based on `get_device_model`
        else:
            pi_model = self.detector.get_device_model()
            if pi_model:
                pi_model = pi_model.upper().replace(" ", "_")
                if "PLUS" in pi_model:
                    re_model = re.search(r"(RASPBERRY_PI_\d).*([AB]_*)(PLUS)", pi_model)
                elif "CM" in pi_model:  # untested for Compute Module
                    re_model = re.search(r"(RASPBERRY_PI_CM)(\d)", pi_model)
                else:  # untested for non-plus models
                    re_model = re.search(r"(RASPBERRY_PI_\d).*([AB])", pi_model)

                if re_model:
                    pi_model = "".join(re_model.groups())
                    available_models = boards._PI_REV_CODES.keys()
                    for model in available_models:
                        if model == pi_model:
                            return model

        return None

    def _pi_rev_code(self) -> Optional[str]:
        """Attempt to find a Raspberry Pi revision code for this board."""
        # 2708 is Pi 1
        # 2709 is Pi 2
        # 2835 is Pi 3 (or greater) on 4.9.x kernel
        # Anything else is not a Pi.
        if self.detector.chip.id != chips.BCM2XXX:
            # Something else, not a Pi.
            return None
        rev = self.detector.get_cpuinfo_field("Revision")

        if rev is not None:
            return rev

        try:
            with open("/proc/device-tree/system/linux,revision", "rb") as revision:
                rev_bytes = revision.read()

                if rev_bytes[:1] == b"\x00":
                    rev_bytes = rev_bytes[1:]

                return rev_bytes.hex()
        except FileNotFoundError:
            return None

    # pylint: disable=no-self-use
    def _beaglebone_id(self) -> Optional[str]:
        """Try to detect id of a Beaglebone."""
        board_value = self.detector.get_device_compatible()
        # Older Builds
        if "freedom-u74-arty" in board_value:
            return boards.BEAGLEV_STARLIGHT

        # Newer Builds
        if "beaglev-starlight" in board_value:
            return boards.BEAGLEV_STARLIGHT

        try:
            with open("/sys/bus/nvmem/devices/0-00500/nvmem", "rb") as eeprom:
                eeprom_bytes = eeprom.read(16)
        except FileNotFoundError:
            try:
                with open("/sys/bus/nvmem/devices/0-00501/nvmem", "rb") as eeprom:
                    eeprom_bytes = eeprom.read(16)
            except FileNotFoundError:
                return None

        if eeprom_bytes[:4] != b"\xaaU3\xee":
            return None

        # special condition for BeagleBone Green rev. 1A
        # refer to GitHub issue #57 in this repo for more info
        if eeprom_bytes == b"\xaaU3\xeeA335BNLT\x1a\x00\x00\x00":
            return boards.BEAGLEBONE_GREEN

        id_string = eeprom_bytes[4:].decode("ascii")
        for model, bb_ids in boards._BEAGLEBONE_BOARD_IDS.items():
            for bb_id in bb_ids:
                if id_string == bb_id[1]:
                    return model

        board_value = self.detector.get_armbian_release_field("BOARD")
        return None

    # pylint: enable=no-self-use

    def _bbai_id(self) -> Optional[str]:
        """Try to detect id of a Beaglebone AI related board."""
        board_value = self.detector.get_device_model()
        if "BeagleBone AI" in board_value:
            return boards.BEAGLEBONE_AI
        return None

    def _tisk_id(self) -> Optional[str]:
        """Try to detect the id of aarch64 board."""
        compatible = self.detector.get_device_compatible()
        print(compatible)
        if not compatible:
            return None
        compats = compatible.split("\x00")
        for board_id, board_compats in boards._TI_SK_BOARD_IDS:
            if any(v in compats for v in board_compats):
                return board_id
        return None

    # pylint: disable=too-many-return-statements
    def _armbian_id(self) -> Optional[str]:
        """Check whether the current board is an OrangePi board."""
        board_value = self.detector.get_armbian_release_field("BOARD")
        board = None

        if board_value == "orangepipc":
            board = boards.ORANGE_PI_PC
        elif board_value == "orangepi-r1":
            board = boards.ORANGE_PI_R1
        elif board_value == "orangepizero":
            board = boards.ORANGE_PI_ZERO
        elif board_value == "orangepione":
            board = boards.ORANGE_PI_ONE
        elif board_value == "orangepilite":
            board = boards.ORANGE_PI_LITE
        elif board_value == "orangepiplus2e":
            board = boards.ORANGE_PI_PLUS_2E
        elif board_value == "orangepipcplus":
            board = boards.ORANGE_PI_PC_PLUS
        elif board_value == "pinebook-a64":
            board = boards.PINEBOOK
        elif board_value == "pineH64":
            board = boards.PINEH64
        elif board_value == "orangepi2":
            board = boards.ORANGE_PI_2
        elif board_value == "orangepi3":
            board = boards.ORANGE_PI_3
        elif board_value == "orangepi3-lts":
            board = boards.ORANGE_PI_3_LTS
        elif board_value == "orangepi4":
            board = boards.ORANGE_PI_4
        elif board_value == "orangepi4-lts":
            board = boards.ORANGE_PI_4_LTS
        elif board_value == "bananapim2zero":
            board = boards.BANANA_PI_M2_ZERO
        elif board_value == "bananapim2plus":
            board = boards.BANANA_PI_M2_PLUS
        elif board_value == "bananapim5":
            board = boards.BANANA_PI_M5
        elif board_value == "orangepizeroplus2-h5":
            board = boards.ORANGE_PI_ZERO_PLUS_2H5
        elif board_value == "orangepizeroplus":
            board = boards.ORANGE_PI_ZERO_PLUS
        elif board_value == "orangepizero2":
            board = boards.ORANGE_PI_ZERO_2
        elif board_value == "nanopiair":
            board = boards.NANOPI_NEO_AIR
        elif board_value == "nanopiduo2":
            board = boards.NANOPI_DUO2
        elif board_value == "nanopineo":
            board = boards.NANOPI_NEO
        elif board_value == "nezha":
            board = boards.LICHEE_RV
        elif board_value == "pcduino2":
            board = boards.PCDUINO2
        elif board_value == "pcduino3":
            board = boards.PCDUINO3

        return board

    # pylint: enable=too-many-return-statements

    # pylint: enable=too-many-return-statements

    def _sama5_id(self) -> Optional[str]:
        """Check what type sama5 board."""
        board_value = self.detector.get_device_model()
        if "Giant Board" in board_value:
            return boards.GIANT_BOARD
        return None

    def _s905x3_id(self) -> Optional[str]:
        """Check what type S905X3 board."""
        board_value = self.detector.get_device_model()
        if "Bananapi BPI-M5" in board_value:
            return boards.BANANA_PI_M5
        return boards.ODROID_C4

    def _stm32mp1_id(self) -> Optional[str]:
        """Check what type stm32mp1 board."""
        board_value = self.detector.get_device_model()
        if "STM32MP157C-DK2" in board_value:
            return boards.STM32MP157C_DK2
        if "LubanCat" in board_value:
            return boards.LUBANCAT_STM32MP157
        if "OSD32MP1-BRK" in board_value:
            return boards.OSD32MP1_BRK
        if "OSD32MP1-RED" in board_value:
            return boards.OSD32MP1_RED
        if "STM32MP1XX OLinuXino" in board_value:
            return boards.STMP157_OLINUXINO_LIME2
        return None

    def _imx8mx_id(self) -> Optional[str]:
        """Check what type iMX8M board."""
        board_value = self.detector.get_device_model()
        if "FSL i.MX8MM DDR4 EVK" in board_value:
            return boards.MAAXBOARD_MINI
        if "Freescale i.MX8MQ EVK" in board_value:
            return boards.MAAXBOARD
        if "Phanbell" in board_value:
            return boards.CORAL_EDGE_TPU_DEV
        return None

    def _imx6ull_id(self) -> Optional[str]:
        """Check what type iMX6ULL board."""
        board_value = self.detector.get_device_model()
        if "LubanCat" in board_value or "Embedfire" in board_value:
            return boards.LUBANCAT_IMX6ULL
        return None

    def _tegra_id(self) -> Optional[str]:
        """Try to detect the id of aarch64 board."""
        compatible = self.detector.get_device_compatible()
        if not compatible:
            return None
        compats = compatible.split("\x00")
        for board_id, board_compats in boards._JETSON_IDS:
            if any(v in compats for v in board_compats):
                return board_id
        return None

    def _sifive_id(self) -> Optional[str]:
        """Try to detect the id for Sifive RISCV64 board."""
        board_value = self.detector.get_device_model()
        if "hifive-unleashed-a00" in board_value:
            return boards.SIFIVE_UNLEASHED
        return None

    def _allwinner_id(self) -> Optional[str]:
        """Try to detect the id for Allwiner D1 board."""
        board_value = self.detector.get_device_model()
        if "sun20iw1p1" in board_value:
            return boards.ALLWINER_D1
        return None

    def _pine64_id(self) -> Optional[str]:
        """Try to detect the id for Pine64 board or device."""
        board_value = self.detector.get_device_model()
        board = None
        if "pine64" in board_value.lower():
            board = boards.PINE64
        elif "pine h64" in board_value.lower():
            board = boards.PINEH64
        elif "pinebook" in board_value.lower():
            board = boards.PINEBOOK
        elif "pinephone" in board_value.lower():
            board = boards.PINEPHONE
        elif "sopine" in board_value.lower():
            board = boards.SOPINE
        return board

    # pylint: disable=no-self-use
    def _pynq_id(self) -> Optional[str]:
        """Try to detect the id for Xilinx PYNQ boards."""
        try:
            with open(
                "/proc/device-tree/chosen/pynq_board", "r", encoding="utf-8"
            ) as board_file:
                board_model = board_file.read()
                match = board_model.upper().replace("-", "_").rstrip("\x00")
                for model in boards._PYNQ_IDS:
                    if model == match:
                        return model

                return None

        except FileNotFoundError:
            return None

    def _rk3566_id(self) -> Optional[str]:
        """Check what type of rk3566 board."""
        board_value = self.detector.get_device_model()
        board = None
        if board_value and "LubanCat-Zero" in board_value:
            board = boards.LUBANCAT_ZERO
        if board_value and "LubanCat1" in board_value:
            board = boards.LUBANCAT1
        if board_value and "Radxa CM3 IO" in board_value:
            board = boards.RADXA_CM3
        return board

    def _rk3568_id(self) -> Optional[str]:
        """Check what type of rk3568 board."""
        board_value = self.detector.get_device_model()
        board = None
        if board_value and "LubanCat2" in board_value:
            board = boards.LUBANCAT2
        return board

    def _rock_pi_id(self) -> Optional[str]:
        """Check what type of Rock Pi board."""
        board_value = self.detector.get_device_model()
        board = None
        if board_value and "ROCK Pi S" in board_value:
            board = boards.ROCK_PI_S
        if board_value and "ROCK PI 4" in board_value.upper():
            board = boards.ROCK_PI_4
        if board_value and "ROCK PI E" in board_value.upper():
            board = boards.ROCK_PI_E
        if self.detector.check_board_name_value() == "ROCK Pi X":
            board = boards.ROCK_PI_X
        if board_value and "ROCK 5" in board_value.upper():
            board = boards.ROCK_PI_5
        if board_value and "RADXA ROCK 4C+" in board_value.upper():
            board = boards.ROCK_PI_4_C_PLUS
        return board

    def _clockwork_pi_id(self) -> Optional[str]:
        """Check what type of Clockwork Pi board."""
        board_value = self.detector.get_device_model()
        board = None
        if board_value and "Clockwork CPI3" in board_value:
            board = boards.CLOCKWORK_CPI3
        return board

    def _udoo_id(self) -> Optional[str]:
        """Try to detect the id of udoo board."""
        board_asset_tag = self.detector.check_board_asset_tag_value()
        for board_id, board_tags in boards._UDOO_BOARD_IDS.items():
            if any(v == board_asset_tag for v in board_tags):
                return board_id

        if self.detector.check_board_name_value() == "UDOO x86":
            return boards.UDOO_X86

        return None

    def _j4105_id(self) -> Optional[str]:
        """Try to detect the id of J4105 board."""
        try:
            with open(
                "/sys/devices/virtual/dmi/id/board_name", "r", encoding="utf-8"
            ) as board_name:
                board_value = board_name.read().rstrip()
            if board_value in ("ODYSSEY-X86J41X5", "ODYSSEY-X86J41O5"):
                return boards.ODYSSEY_X86J41X5
            return None
        except FileNotFoundError:
            return None

    def _asus_tinker_board_id(self) -> Optional[str]:
        """Check what type of Tinker Board."""
        board_value = self.detector.get_device_model()
        board = None
        if board_value and "ASUS Tinker Board" in board_value:
            board = boards._ASUS_TINKER_BOARD_IDS
        return board

    def _pcduino_board_id(self) -> Optional[str]:
        """Check on the type of Pcduino"""
        board_value = self.detector.get_device_model()
        board = None
        if "pcduino2" in board_value.lower():
            board = boards.PCDUINO2
        if "pcduino3" in board_value.lower():
            board = boards.PCDUINO3
        return board

    def _allwinner_variants_id(self) -> Optional[str]:
        """Try to detect the id of allwinner based board. (orangepi, nanopi)"""
        board_value = self.detector.get_device_model()
        board = None
        if not board_value:
            return board
        board_value = board_value.lower()
        chip_id = self.detector.chip.id
        if "nanopi" in board_value:
            if "neo" in board_value and "SUN8I" in chip_id:
                board = boards.NANOPI_NEO_AIR
            # TODO: Add other specifc board contexts here
        elif "orange pi" in board_value:
            if "zero" in board_value:
                if "H5" in chip_id:
                    board = boards.ORANGE_PI_ZERO_PLUS_2H5
                elif "H616" in chip_id:
                    board = boards.ORANGE_PI_ZERO_2
            # TODO: Add other specifc board contexts here
        return board

    def _rp2040_u2if_id(self) -> Optional[str]:
        import hid

        # look for it based on PID/VID
        for dev in hid.enumerate():
            # Raspberry Pi Pico
            vendor = dev["vendor_id"]
            product = dev["product_id"]
            if vendor == 0xCAFE and product == 0x4005:
                return boards.PICO_U2IF
            if vendor == 0x239A:
                # Feather RP2040
                if product == 0x00F1:
                    return boards.FEATHER_U2IF
                # Itsy Bitsy RP2040
                if product == 0x00FD:
                    return boards.ITSYBITSY_U2IF
                # QT Py RP2040
                if product == 0x00F7:
                    return boards.QTPY_U2IF
                # QT2040 Trinkey
                if product == 0x0109:
                    return boards.QT2040_TRINKEY_U2IF
                # MacroPad RP2040
                if product == 0x0107:
                    return boards.MACROPAD_U2IF
        # Will only reach here if a device was added in chip.py but here.
        raise RuntimeError("RP2040_U2IF device was added to chip but not board.")

    def _siemens_simatic_iot2000_id(self) -> Optional[str]:
        """Try to detect if this is a IOT2050 Gateway."""
        board_value = self.detector.get_device_model()
        board = None
        if board_value and "SIMATIC IOT2050 Advanced" in board_value:
            board = boards.SIEMENS_SIMATIC_IOT2050_ADV
        elif board_value and "SIMATIC IOT2050 Basic" in board_value:
            board = boards.SIEMENS_SIMATIC_IOT2050_BASIC
        return board

    @property
    def any_siemens_simatic_iot2000(self) -> bool:
        """Check whether the current board is a SIEMENS SIMATIC IOT2000 Gateway."""
        return self.id in boards._SIEMENS_SIMATIC_IOT2000_IDS

    @property
    def any_nanopi(self) -> bool:
        """Check whether the current board is any defined Nano Pi."""
        return self.id in boards._NANOPI_IDS

    @property
    def any_96boards(self) -> bool:
        """Check whether the current board is any 96boards board."""
        return self.id in boards._LINARO_96BOARDS_IDS

    @property
    def any_raspberry_pi(self) -> bool:
        """Check whether the current board is any Raspberry Pi."""
        return self._pi_rev_code() is not None

    @property
    def any_raspberry_pi_40_pin(self) -> bool:
        """Check whether the current board is any 40-pin Raspberry Pi."""
        return self.id in boards._RASPBERRY_PI_40_PIN_IDS

    @property
    def any_raspberry_pi_cm(self) -> bool:
        """Check whether the current board is any Compute Module Raspberry Pi."""
        return self.id in boards._RASPBERRY_PI_CM_IDS

    @property
    def any_beaglebone(self) -> bool:
        """Check whether the current board is any Beaglebone-family system."""
        return self.id in boards._BEAGLEBONE_IDS

    @property
    def any_orange_pi(self) -> bool:
        """Check whether the current board is any defined Orange Pi."""
        return self.id in boards._ORANGE_PI_IDS

    @property
    def any_lubancat(self) -> bool:
        """Check whether the current board is any defined lubancat."""
        return self.id in boards._LUBANCAT_IDS

    @property
    def any_coral_board(self) -> bool:
        """Check whether the current board is any defined Coral."""
        return self.id in boards._CORAL_IDS

    @property
    def any_pynq_board(self) -> bool:
        """Check whether the current board is any defined PYNQ Board."""
        return self.id in boards._PYNQ_IDS

    @property
    def any_giant_board(self) -> bool:
        """Check whether the current board is any defined Giant Board."""
        return self.GIANT_BOARD

    @property
    def any_odroid_40_pin(self) -> bool:
        """Check whether the current board is any defined 40-pin Odroid."""
        return self.id in boards._ODROID_40_PIN_IDS

    @property
    def khadas_vim3_40_pin(self) -> bool:
        """Check whether the current board is any defined 40-pin Khadas VIM3."""
        return self.id in boards._KHADAS_40_PIN_IDS

    @property
    def any_jetson_board(self) -> bool:
        """Check whether the current board is any defined Jetson Board."""
        return self.id in [v[0] for v in boards._JETSON_IDS]

    @property
    def any_sifive_board(self) -> bool:
        """Check whether the current board is any defined Jetson Board."""
        return self.id in boards._SIFIVE_IDS

    @property
    def any_onion_omega_board(self) -> bool:
        """Check whether the current board is any defined OpenWRT board."""
        return self.id in boards._ONION_OMEGA_BOARD_IDS

    @property
    def any_pine64_board(self) -> bool:
        """Check whether the current board is any Pine64 device."""
        return self.id in boards._PINE64_DEV_IDS

    @property
    def any_rock_pi_board(self) -> bool:
        """Check whether the current board is any Rock Pi device."""
        return self.id in boards._ROCK_PI_IDS

    @property
    def any_clockwork_pi_board(self) -> bool:
        """Check whether the current board is any Clockwork Pi device."""
        return self.CLOCKWORK_CPI3

    @property
    def any_udoo_board(self) -> bool:
        """Check to see if the current board is an UDOO board"""
        return self.id in boards._UDOO_BOARD_IDS

    @property
    def any_seeed_board(self) -> bool:
        """Check to see if the current board is an SEEED board"""
        return self.id in boards._SEEED_BOARD_IDS

    @property
    def any_asus_tinker_board(self) -> bool:
        """Check to see if the current board is an ASUS Tinker Board"""
        return self.id in boards._ASUS_TINKER_BOARD_IDS

    @property
    def any_pcduino_board(self) -> bool:
        """Check whether the current board is any Pcduino board"""
        return self.id in boards._PCDUINO_DEV_IDS

    @property
    def any_stm32mp1(self) -> bool:
        """Check whether the current board is any stm32mp1 board."""
        return self.id in boards._STM32MP1_IDS

    @property
    def any_bananapi(self) -> bool:
        """Check whether the current board is any BananaPi-family system."""
        return self.id in boards._BANANA_PI_IDS

    @property
    def any_maaxboard(self) -> bool:
        """Check whether the current board is any BananaPi-family system."""
        return self.id in boards._MAAXBOARD_IDS

    @property
    def any_tisk_board(self) -> bool:
        """Check whether the current board is any defined TI SK Board."""
        return self.id in [v[0] for v in boards._TI_SK_BOARD_IDS]

    @property
    def any_lichee_riscv_board(self) -> bool:
        """Check whether the current board is any defined Lichee RISC-V."""
        return self.id in boards._LICHEE_RISCV_IDS

    @property
    def any_libre_computer_board(self) -> bool:
        """Check whether the current board is any defined Libre Computer board."""
        return self.id in boards._LIBRE_COMPUTER_IDS

    @property
    def os_environ_board(self) -> bool:
        """Check whether the current board is an OS environment variable special case."""

        def lazily_generate_conditions():
            yield self.board.FTDI_FT232H
            yield self.board.FTDI_FT2232H
            yield self.board.MICROCHIP_MCP2221
            yield self.board.BINHO_NOVA
            yield self.board.GREATFET_ONE
            yield self.board.PICO_U2IF
            yield self.board.FEATHER_U2IF
            yield self.board.ITSYBITY_U2IF
            yield self.board.MACROPAD_U2IF
            yield self.board.QTPY_U2IF
            yield self.board.QT2040_TRINKEY_U2IF

        return any(condition for condition in lazily_generate_conditions())

    @property
    def any_embedded_linux(self) -> bool:
        """Check whether the current board is any embedded Linux device."""

        def lazily_generate_conditions():
            yield self.any_raspberry_pi_40_pin
            yield self.any_raspberry_pi
            yield self.any_beaglebone
            yield self.any_orange_pi
            yield self.any_nanopi
            yield self.any_giant_board
            yield self.any_jetson_board
            yield self.any_coral_board
            yield self.any_odroid_40_pin
            yield self.khadas_vim3_40_pin
            yield self.any_96boards
            yield self.any_sifive_board
            yield self.any_onion_omega_board
            yield self.any_pine64_board
            yield self.any_pynq_board
            yield self.any_rock_pi_board
            yield self.any_clockwork_pi_board
            yield self.any_udoo_board
            yield self.any_seeed_board
            yield self.any_asus_tinker_board
            yield self.any_stm32mp1
            yield self.any_lubancat
            yield self.any_bananapi
            yield self.any_maaxboard
            yield self.any_tisk_board
            yield self.any_siemens_simatic_iot2000
            yield self.any_lichee_riscv_board
            yield self.any_pcduino_board
            yield self.any_libre_computer_board
            yield self.generic_linux

        return any(condition for condition in lazily_generate_conditions())

    @property
    def generic_linux(self) -> bool:
        """Check whether the current board is an Generic Linux System."""
        return self.id == boards.GENERIC_LINUX_PC

    @property
    def ftdi_ft232h(self) -> bool:
        """Check whether the current board is an FTDI FT232H."""
        return self.id == boards.FTDI_FT232H

    @property
    def ftdi_ft2232h(self) -> bool:
        """Check whether the current board is an FTDI FT2232H."""
        return self.id == boards.FTDI_FT2232H

    @property
    def microchip_mcp2221(self) -> bool:
        """Check whether the current board is a Microchip MCP2221."""
        return self.id == boards.MICROCHIP_MCP2221

    @property
    def pico_u2if(self) -> bool:
        """Check whether the current board is a RPi Pico w/ u2if."""
        return self.id == boards.PICO_U2IF

    @property
    def feather_u2if(self) -> bool:
        """Check whether the current board is a Feather RP2040 w/ u2if."""
        return self.id == boards.FEATHER_U2IF

    @property
    def itsybitsy_u2if(self) -> bool:
        """Check whether the current board is a Itsy Bitsy w/ u2if."""
        return self.id == boards.ITSYBITSY_U2IF

    @property
    def macropad_u2if(self) -> bool:
        """Check whether the current board is a MacroPad w/ u2if."""
        return self.id == boards.MACROPAD_U2IF

    @property
    def qtpy_u2if(self) -> bool:
        """Check whether the current board is a QT Py w/ u2if."""
        return self.id == boards.QTPY_U2IF

    @property
    def qt2040_trinkey_u2if(self) -> bool:
        """Check whether the current board is a QT Py w/ u2if."""
        return self.id == boards.QT2040_TRINKEY_U2IF

    @property
    def binho_nova(self) -> bool:
        """Check whether the current board is an BINHO NOVA."""
        return self.id == boards.BINHO_NOVA

    @property
    def greatfet_one(self) -> bool:
        """Check whether the current board is a GreatFET One."""
        return self.id == boards.GREATFET_ONE

    def __getattr__(self, attr: str) -> bool:
        """
        Detect whether the given attribute is the currently-detected board.  See list
        of constants at the top of this module for available options.
        """
        if self.id == attr:
            return True
        return False
