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
import RPi.GPIO as GPIO
import time

from sj201_interface.revisions import SJ201


class MycroftSwitch:
    """ abstract base class for a Mycroft Switch Array
     all switches must provide at least these basic methods """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def terminate(self):
        """terminates any underlying threads"""
        return

    @abc.abstractmethod
    def handle_action(self, *args):
        return

    @abc.abstractmethod
    def handle_vol_down(self, *args):
        return

    @abc.abstractmethod
    def handle_vol_up(self, *args):
        return

    @abc.abstractmethod
    def handle_mute(self, *args):
        return

    @abc.abstractmethod
    def get_capabilities(self):
        return


class R6Switches(MycroftSwitch):
    """
    Class to handle the Mark2 switches.
    Note - a switch is an abstract concept
    which applies to buttons and switches.
    The Mark2 actually has 4 different switches.
    Three buttons (volume up, down and activate)
    and a mute mic switch. All are read only
    and interrupt driven. Also note switches are
    pulled up so the active state is actually zero.
    """
    # sj201R6 and R10
    _SW_VOL_UP = 22
    _SW_VOL_DOWN = 23
    _SW_ACTION = 24
    _SW_MUTE = 25

    def __init__(self, debounce=100):
        self.debounce = debounce
        self.active = 0

        # some switch implementations require a thread
        # we don't but we must meet the base requirement
        self.thread_handle = None

        self.capabilities = {
            "user_volup_handler": "button",
            "user_voldown_handler": "button",
            "user_action_handler": "button",
            "user_mute_handler": "slider"
        }

        # use BCM GPIO pin numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # we need to pull up the 3 buttons and mute switch
        GPIO.setup(self._SW_ACTION, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._SW_VOL_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._SW_VOL_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._SW_MUTE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # establish default values
        self.SW_ACTION = GPIO.input(self._SW_ACTION)
        self.SW_VOL_UP = GPIO.input(self._SW_VOL_UP)
        self.SW_VOL_DOWN = GPIO.input(self._SW_VOL_DOWN)
        self.SW_MUTE = GPIO.input(self._SW_MUTE)

        # attach callbacks
        GPIO.add_event_detect(self._SW_ACTION,
                              GPIO.BOTH,
                              callback=self.handle_action,
                              bouncetime=debounce)

        GPIO.add_event_detect(self._SW_VOL_UP,
                              GPIO.BOTH,
                              callback=self.handle_vol_up,
                              bouncetime=debounce)

        GPIO.add_event_detect(self._SW_VOL_DOWN,
                              GPIO.BOTH,
                              callback=self.handle_vol_down,
                              bouncetime=debounce)

        GPIO.add_event_detect(self._SW_MUTE,
                              GPIO.BOTH,
                              callback=self.handle_mute,
                              bouncetime=debounce)

        # user overrides
        self.user_voldown_handler = None
        self.user_volup_handler = None
        self.user_action_handler = None
        self.user_mute_handler = None

    def get_capabilities(self):
        return self.capabilities

    def handle_action(self, channel):
        self.SW_ACTION = GPIO.input(self._SW_ACTION)
        if self.SW_ACTION == self.active:
            if self.user_action_handler is not None:
                self.user_action_handler()

    def handle_vol_up(self, channel):
        self.SW_VOL_UP = GPIO.input(self._SW_VOL_UP)
        if self.SW_VOL_UP == self.active:
            if self.user_volup_handler is not None:
                self.user_volup_handler()

    def handle_vol_down(self, channel):
        self.SW_VOL_DOWN = GPIO.input(self._SW_VOL_DOWN)
        if self.SW_VOL_DOWN == self.active:
            if self.user_voldown_handler is not None:
                self.user_voldown_handler()

    def handle_mute(self, channel):
        # No idea why this delay is necessary, but it makes the muting reliable
        time.sleep(0.05)
        self.SW_MUTE = GPIO.input(self._SW_MUTE)

        if self.user_mute_handler is not None:
            self.user_mute_handler(self.SW_MUTE)

    def terminate(self):
        pass


def get_switches(revision: SJ201) -> MycroftSwitch:
    """
    Get a MycroftSwitch object to handle action and volume controls
    :param revision: SJ201 Board Revision
    :returns: MycroftSwitch Object
    """
    if revision == SJ201.r10:
        return R6Switches()
    elif revision == SJ201.r6:
        return R6Switches()
    else:
        raise ValueError(f"Unsupported revision: {revision}")
