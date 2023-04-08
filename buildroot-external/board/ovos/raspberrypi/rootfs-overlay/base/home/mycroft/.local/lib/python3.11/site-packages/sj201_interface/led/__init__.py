# Copyright 2020 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import abc
from typing import Union

import board
import neopixel

from enum import Enum
from time import sleep
from threading import Thread, Event
from queue import Queue
from ovos_utils.log import LOG
from smbus2.smbus2 import SMBus, I2C_SMBUS_BLOCK_MAX

from sj201_interface.revisions import SJ201, detect_sj201_revision


class Palette(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    MAGENTA = (255, 0, 255)
    BURNT_ORANGE = (173, 64, 0)
    MYCROFT_RED = (216, 17, 89)
    MYCROFT_GREEN = (64, 219, 176)
    MYCROFT_BLUE = (34, 167, 240)


class MycroftLed:
    """abstract base class for a Mycroft Led
    all leds must provide at least these basic methods"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        return

    @property
    @abc.abstractmethod
    def num_leds(self) -> int:
        """
        Return the number of logical LED's available
        """
        return 0

    @abc.abstractmethod
    def set_led(self, which_led, color, immediate=True):
        """Set the color of a specific LED.
        Arguments:
         which_led (Int): the index of the LED to be changed
         color (Tuple): the RGB color as a three integer Tuple
         immediate (Bool): whether to change now or wait for the next call of show()
        """
        return

    @abc.abstractmethod
    def fill(self, color):
        """set all leds to the supplied color
        Arguments:
         color (Tuple): the RGB color as a three integer Tuple
        """
        return

    @abc.abstractmethod
    def show(self):
        """update leds from buffered data"""
        return

    @abc.abstractmethod
    def get_led(self, which_led):
        """returns current buffered value"""
        return

    @abc.abstractmethod
    def set_leds(self, leds):
        """updates buffer from leds and update hardware
        Arguments:
         leds [(of tuples),()]: the RGB color as a three integer Tuple
        """
        return

    @abc.abstractmethod
    def get_capabilities(self):
        """returns capabilities object"""
        return

    @staticmethod
    def adjust_brightness(cval, bval):
        return min(255, cval * bval)


class R6Led(MycroftLed):
    real_num_leds = 12  # physical
    _num_leds = 12  # logical
    black = Palette.BLACK
    device_addr = 0x04

    def __init__(self):
        self.bus = SMBus(1)
        self.brightness = 0.5
        self.capabilities = {
            "num_leds": self.num_leds,
            "brightness": "(0.0-1.0)",
            "led_colors": "MycroftPalette",
            "reserved_leds": list(
                range(self.num_leds, self.real_num_leds)
            ),
        }

    @property
    def num_leds(self):
        return self._num_leds

    def get_capabilities(self):
        return self.capabilities

    def _set_led(self, pixel, color):
        """ internal interface
            permits access to the
            reserved leds """
        red_val = int(color[0])
        green_val = int(color[1])
        blue_val = int(color[2])

        # cmd =   "i2cset -y 1 %d %d %d %d %d i " % (
        #             self.device_addr,
        #             pixel,
        #             red_val,
        #             green_val,
        #             blue_val)
        # os.system(cmd)
        # LOG.debug("Execute %s" % (cmd,))

        self.bus.write_i2c_block_data(
            self.device_addr, pixel,
            [red_val, green_val, blue_val]
        )

    def _set_led_with_brightness(self, pixel, color, blevel):
        self._set_led(
            pixel,
            list(
                map(
                    self.adjust_brightness,
                    color,
                    (blevel,) * 3)))

    def show(self):
        """ show buffered leds, only used
           for older slower devices """
        pass

    def set_led(self, pixel, color, immediate=True):
        """ external interface enforces led
            reservation and honors brightness """
        self._set_led(
            pixel % self.num_leds,
            list(
                map(
                    self.adjust_brightness,
                    color,
                    (self.brightness,) * 3)))

    def get_led(self, which_led):
        pass

    def fill(self, color: Union[tuple, Palette]):
        """fill all leds with the same color"""
        if isinstance(color, Palette):
            color = color.value
        rgb = [int(self.adjust_brightness(c, self.brightness))
               for c in color[:3]]
        try:
            # Each element in rgb is a 3 byte tuple
            led_per_block = int(str(I2C_SMBUS_BLOCK_MAX / 3).split('.')[0])
        except Exception as e:
            LOG.exception(e)
            led_per_block = 10
        leds_to_write = self.num_leds
        last_written_idx = 0
        LOG.debug(f"Writing {leds_to_write} LEDs in blocks of {led_per_block}")
        while leds_to_write > led_per_block:
            leds_to_write = leds_to_write - led_per_block
            self.bus.write_i2c_block_data(
                self.device_addr, last_written_idx,
                rgb * led_per_block
            )
            last_written_idx += led_per_block
        if leds_to_write > 0:
            self.bus.write_i2c_block_data(
                self.device_addr, last_written_idx,
                rgb * leds_to_write
            )

    def set_leds(self, new_leds):
        """set leds from tuple array"""
        for x in range(0, self.num_leds):
            self.set_led(x, new_leds[x])


class R10Led(MycroftLed):
    led_type = 'new'
    real_num_leds = 12  # physical
    _num_leds = 12  # logical
    black = Palette.BLACK

    def __init__(self):
        # pixel_pin = board.D12
        # order = neopixel.GRB
        self.brightness = 0.2
        self.pixels = neopixel.NeoPixel(
            board.D12,
            self.real_num_leds,
            brightness=self.brightness,
            auto_write=False,
            pixel_order=neopixel.GRB
        )

        self.capabilities = {
            "num_leds": self.num_leds,
            "brightness": "(0.0-1.0)",
            "led_colors": "MycroftPalette",
            "reserved_leds": list(range(self.num_leds, self.real_num_leds)),
        }

    @property
    def num_leds(self):
        return self._num_leds

    def get_capabilities(self):
        return self.capabilities

    def _set_led(self, pixel, color):
        """internal interface
        permits access to the
        reserved leds"""
        red_val = int(color[0])
        green_val = int(color[1])
        blue_val = int(color[2])
        self.pixels[pixel] = (red_val, green_val, blue_val)

    def _set_led_with_brightness(self, pixel, color, blevel):
        self._set_led(pixel, list(map(self.adjust_brightness,
                                      color, (blevel,) * 3)))

    def show(self):
        """show buffered leds, only used
        for older slower devices"""
        self.pixels.show()

    def set_led(self, pixel, color, immediate=True):
        """external interface enforces led
        reservation and honors brightness"""
        LOG.debug(f"setting {pixel} to {color}")
        self._set_led(
            pixel % self.num_leds,
            list(map(self.adjust_brightness, color, (self.brightness,) * 3)),
        )
        if immediate:
            self.pixels.show()

    def get_led(self, which_led):
        pass

    def fill(self, color: tuple):
        """fill all leds with the same color"""
        rgb = [int(self.adjust_brightness(c, self.brightness))
               for c in color[:3]]
        self.pixels.fill(rgb)
        self.pixels.show()

    def set_leds(self, new_leds):
        """set leds from tuple array"""
        for x in range(0, self.num_leds):
            self.set_led(x, new_leds[x])


class LedThread(Thread):
    def __init__(self, led_obj, animations=None):
        self.led_obj = led_obj
        self.exit_flag = Event()
        self.animations = animations or {}
        self.queue = Queue()
        self.animation_running = False
        self.animation_name = None
        self._context: {}

        super().__init__()

    def start_animation(self, name: str):
        self.stop_animation()
        self.queue.put(name)

    def stop_animation(self, name=None):
        if name and (self.animation_name != name):
            # Different animation is playing
            return

        self.animation_running = False

    @property
    def context(self):
        return self._context

    def run(self):
        try:
            while not self.exit_flag.wait(30):
                self.animation_name = None
                self.animation_running = False

                name = self.queue.get()
                current_animation = self.animations.get(name)

                if current_animation is not None:
                    try:
                        self._context = {}
                        self.animation_name = name
                        self.animation_running = True
                        current_animation.start()
                        while self.animation_running and current_animation.step(
                                context=self._context
                        ):
                            sleep(0)
                        current_animation.stop()
                    except Exception as e:
                        self.led_obj.fill(self.led_obj.black)
                        LOG.exception(f"error running animation '{name}': {e}")

                else:
                    LOG.error(f"No animation named {name}")
        except Exception as e:
            LOG.exception(f"error running led animation: {e}")


def get_led(revision: SJ201) -> MycroftLed:
    """
    Get a MycroftLed object to handle LED controls
    :param revision: SJ201 Board Revision
    :returns: MycroftLed Object
    """
    if revision == SJ201.r10:
        return R10Led()
    elif revision == SJ201.r6:
        return R6Led()
    else:
        raise ValueError(f"Unsupported revision: {revision}")


def chase(led: MycroftLed = None, color: Palette = Palette.WHITE):
    """
    Display a color chase animation of the Mark2 LED Ring
    :param led: MycroftLed object, else detect platform and create one
    :param color: Palette color to chase
    """
    led = led or get_led(detect_sj201_revision())
    for i in range(led.num_leds):
        led.set_led(i, color.value)
        sleep(0.02)


def reset_led_animation(color: Palette = Palette.WHITE):
    """
    Show a chase animation to fill and then clear the LEDs
    :param color: Fill color
    """
    led_object = get_led(detect_sj201_revision())
    chase(led_object, color)
    sleep(1)
    chase(led_object, Palette.BLACK)
