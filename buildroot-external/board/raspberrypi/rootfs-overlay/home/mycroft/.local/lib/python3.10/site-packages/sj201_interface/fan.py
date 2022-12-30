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
import subprocess
import RPi.GPIO as GPIO

from time import sleep
from threading import Thread, Event
from ovos_utils.log import LOG
from sj201_interface.revisions import SJ201, detect_sj201_revision


class MycroftFan:
    """ abstract base class for a Mycroft Fan
     all fan classes must provide at least
     these basic methods """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_fan_speed(self, new_speed):
        """takes in value between 0 - 100
           converts to internal format"""
        return

    @abc.abstractmethod
    def get_fan_speed(self):
        """returns value between 0-100"""

    @abc.abstractmethod
    def get_cpu_temp(self) -> float:
        """returns temp in celsius"""
        return -1.0

    @abc.abstractmethod
    def shutdown(self):
        """shutdown controls and set output to 0"""

    @staticmethod
    def execute_cmd(cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, )
        out, err = process.communicate()
        try:
            out = out.decode("utf8")
        except Exception as e:
            LOG.exception(e)

        try:
            err = err.decode("utf8")
        except Exception as e:
            LOG.exception(e)

        return out, err

    @staticmethod
    def celcius_to_fahrenheit(temp):
        return (temp * 1.8) + 32


class R6FanControl(MycroftFan):
    # hardware speed range is appx 30-255
    # we convert from 0 to 100
    HDW_MIN = 0
    HDW_MAX = 255
    SFW_MIN = 0
    SFW_MAX = 100

    def __init__(self):
        self.fan_speed = 0
        # self.set_fan_speed(self.fan_speed)

    def speed_to_hdw_val(self, speed):
        out_steps = self.HDW_MAX - self.HDW_MIN
        in_steps = self.SFW_MAX - self.SFW_MIN
        ratio = out_steps / in_steps
        # force compliance
        if speed > self.SFW_MAX:
            speed = self.SFW_MAX
        if speed < self.SFW_MIN:
            speed = self.SFW_MIN

        return int((speed * ratio) + self.HDW_MIN)

    def hdw_val_to_speed(self, hdw_val):
        out_steps = self.SFW_MAX - self.SFW_MIN
        in_steps = self.HDW_MAX - self.HDW_MIN
        ratio = out_steps / in_steps
        # force compliance
        if hdw_val > self.HDW_MAX:
            hdw_val = self.HDW_MAX
        if hdw_val < self.HDW_MIN:
            hdw_val = self.HDW_MIN

        return int(round(((hdw_val - self.HDW_MIN) * ratio) + self.SFW_MIN, 0))

    def hdw_set_speed(self, hdw_speed):
        # force compliance
        if hdw_speed > self.HDW_MAX:
            hdw_speed = self.HDW_MAX
        if hdw_speed < self.HDW_MIN:
            hdw_speed = self.HDW_MIN

        hdw_speed = str(hdw_speed)
        cmd = ["i2cset", "-a", "-y", "1", "0x04", "101", hdw_speed, "i"]
        out, err = self.execute_cmd(cmd)
        LOG.debug(f'out={out}')
        LOG.debug(f'err={err}')

    def set_fan_speed(self, speed):
        self.fan_speed = self.speed_to_hdw_val(speed)
        self.hdw_set_speed(self.fan_speed)

    def get_fan_speed(self):
        return self.hdw_val_to_speed(self.fan_speed)

    def get_cpu_temp(self):
        cmd = ["cat", "/sys/class/thermal/thermal_zone0/temp"]
        out, err = self.execute_cmd(cmd)
        return float(out.strip()) / 1000

    def shutdown(self):
        self.set_fan_speed(0)


class R10FanControl(MycroftFan):
    # hardware speed range is appx 30-255
    # we convert from 0 to 100
    HDW_MIN = 100
    HDW_MAX = 0
    SFW_MIN = 0
    SFW_MAX = 100

    def __init__(self):
        self.fan_speed = 0
        self.fan_pin = 13  # PWM pin connected to Fan
        GPIO.setwarnings(False)  # disable warnings
        GPIO.setmode(GPIO.BCM)  # set pin numbering system
        GPIO.setup(self.fan_pin, GPIO.OUT)  # set direction
        self.pi_pwm = GPIO.PWM(self.fan_pin, 1000)  # create PWM instance with frequency
        self.pi_pwm.start(100)  # start PWM of required Duty Cycle

    @staticmethod
    def speed_to_hdw_val(speed):
        return float(100.0 - (speed % 101))

    @staticmethod
    def hdw_val_to_speed(hdw_val):
        return abs(float(hdw_val - 100.0))

    def hdw_set_speed(self, hdw_speed):
        LOG.debug(f'Setting Fan Duty Cycle to {hdw_speed}')
        self.pi_pwm.ChangeDutyCycle(hdw_speed)  # provide duty cycle in the range 0-100
        sleep(1)  # Block while fan ramps up/down

    def set_fan_speed(self, speed):
        self.fan_speed = self.speed_to_hdw_val(speed)
        self.hdw_set_speed(self.fan_speed)

    def get_fan_speed(self):
        return self.hdw_val_to_speed(self.fan_speed)

    def get_cpu_temp(self):
        cmd = ["cat", "/sys/class/thermal/thermal_zone0/temp"]
        out, err = self.execute_cmd(cmd)
        return float(out.strip()) / 1000

    def shutdown(self):
        self.pi_pwm.stop()
        sleep(1)
        GPIO.output(self.fan_pin, 1)


class FanControlThread(Thread):
    def __init__(self, fan_obj: MycroftFan = None):
        self.fan_obj = fan_obj or get_fan(detect_sj201_revision())
        self.exit_flag = Event()
        self._max_fanless_temp = 60.0
        Thread.__init__(self)

    def run(self):
        LOG.debug("temperature monitor thread started")
        while not self.exit_flag.wait(30):
            LOG.debug(f"CPU temperature is {self.fan_obj.get_cpu_temp()}")

            current_temp = self.fan_obj.get_cpu_temp()
            if current_temp < self._max_fanless_temp:
                # Below specified fanless temperature
                fan_speed = 0
                LOG.debug(f"Temp below {self._max_fanless_temp}")
            elif current_temp > 80.0:
                LOG.warning(f"Thermal Throttling, temp={current_temp}C")
                fan_speed = 100
            else:
                # Specify linear fan curve inside normal operating temp range
                speed_const = 100/(80.0-self._max_fanless_temp)
                fan_speed = speed_const * (current_temp -
                                           self._max_fanless_temp)
                LOG.debug(f"temp={current_temp}")

            LOG.debug(f"Setting fan speed to: {fan_speed}")
            self.fan_obj.set_fan_speed(fan_speed)


def get_fan(revision: SJ201) -> MycroftFan:
    """
    Get a MycroftFan object to handle temperature monitoring and fan controls
    :param revision: SJ201 Board Revision
    :returns: MycroftFan Object
    """
    if revision == SJ201.r10:
        return R10FanControl()
    elif revision == SJ201.r6:
        return R6FanControl()
    else:
        raise ValueError(f"Unsupported revision: {revision}")
