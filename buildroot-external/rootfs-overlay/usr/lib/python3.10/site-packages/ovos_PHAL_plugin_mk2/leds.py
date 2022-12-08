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
import abc
import threading
import typing
from queue import Queue

import time
from ovos_utils.log import LOG
from smbus2.smbus2 import SMBus, I2C_SMBUS_BLOCK_MAX


class Palette:
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
    """ abstract base class for a Mycroft Led
     all leds must provide at least these basic methods """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        return

    @abc.abstractmethod
    def set_led(self, which_led, color, immediate):
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


class Led(MycroftLed):
    real_num_leds = 12  # physical
    num_leds = 12  # logical
    black = (0, 0, 0)  # TODO pull from palette
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

    def adjust_brightness(self, cval, bval):
        return min(255, cval * bval)

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

    def set_led(self, pixel, color):
        """ external interface enforces led
            reservation and honors brightness """
        self._set_led(
            pixel % self.num_leds,
            list(
                map(
                    self.adjust_brightness,
                    color,
                    (self.brightness,) * 3)))

    def fill(self, color):
        """fill all leds with the same color"""

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


class LedAnimation:
    """Base class for LED animations"""

    def __init__(self, led_obj):
        self.led_obj = led_obj

    def start(self):
        """Begin LED animation"""
        pass

    def step(self, context: typing.Dict[str, typing.Any]) -> bool:
        """Single step of the animation.

        Put time.sleep inside here.

        Arguments:
            context: dict with user-defined values

        Returns:
            True if animation should continue
        """
        return False

    def stop(self):
        """End LED animation"""
        pass


class PulseLedAnimation(LedAnimation):
    def __init__(self, led_obj, pal_obj):
        super().__init__(led_obj)

        self.pal_obj = pal_obj
        self.exit_flag = False
        self.color_tup = self.pal_obj.MYCROFT_GREEN
        self.delay = 0.1
        self.brightness = 100
        self.step_size = 5
        self.tmp_leds = []

    def start(self):
        self.led_obj.fill(self.color_tup)

        self.brightness = 100
        self.led_obj.brightness = self.brightness / 100
        self.led_obj.fill(self.color_tup)

    def step(self, context):
        if (self.brightness + self.step_size) > 100:
            self.brightness = self.brightness - self.step_size
            self.step_size = self.step_size * -1

        elif (self.brightness + self.step_size) < 0:
            self.brightness = self.brightness - self.step_size
            self.step_size = self.step_size * -1

        else:
            self.brightness += self.step_size

        self.led_obj.brightness = self.brightness / 100
        self.led_obj.fill(self.color_tup)

        time.sleep(self.delay)
        return True

    def stop(self):
        self.led_obj.brightness = 1.0
        self.led_obj.fill(self.pal_obj.BLACK)


class ChaseLedAnimation(LedAnimation):
    def __init__(self, led_obj, background_color, foreground_color):
        super().__init__(led_obj)

        self.bkgnd_col = background_color
        self.fgnd_col = foreground_color
        self.exit_flag = False
        self.color_tup = foreground_color
        self.delay = 0.1

    def start(self):
        self.led_obj.fill(self.fgnd_col)

    def step(self, context):
        fgnd_col = context.get("chase.foreground_color", self.fgnd_col)
        bkgnd_col = context.get("chase.background_color", self.bkgnd_col)
        stop = context.get("chase.stop", False)

        for x in range(0, 10):
            self.led_obj.set_led(x, fgnd_col)
            time.sleep(self.delay)
            self.led_obj.set_led(x, bkgnd_col)

        if stop:
            return False

        return True

    def stop(self):
        self.led_obj.fill(self.led_obj.black)


class LedThread(threading.Thread):
    def __init__(self, led_obj, animations=None):
        self.led_obj = led_obj
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
            while True:
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
                            time.sleep(0)
                        current_animation.stop()
                    except Exception:
                        self.led_obj.fill(self.led_obj.black)
                        LOG.exception("error running animation '%s'", name)

                else:
                    LOG.error("No animation named %s", name)
        except Exception:
            LOG.exception("error running led animation")
