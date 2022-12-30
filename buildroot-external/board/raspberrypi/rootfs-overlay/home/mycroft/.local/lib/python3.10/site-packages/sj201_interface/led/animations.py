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

import typing
import time


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
