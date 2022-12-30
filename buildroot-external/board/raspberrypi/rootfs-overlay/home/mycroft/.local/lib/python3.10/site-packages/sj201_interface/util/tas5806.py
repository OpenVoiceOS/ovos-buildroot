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

##########################################################################
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
##########################################################################
import os
import time
from math import log, exp
from smbus2 import SMBus
from ovos_utils.log import LOG


class Tas5806:
    devAddr = 0x2f
    MAX_VOL = 84

    def __init__(self):
        self.bus = SMBus(1)

    def dump_data(self):
        # for i in range(0x10):
        #    b = self.bus.read_byte_data(self.devAddr, i)
        #    LOG.debug("%s: %s" % (hex(i), hex(b)) )

        # LOG.debug("------------------")
        command_send = 'i2cdump -y 1 ' + str(self.devAddr) + ' W'
        # os.system(command_send)
        command_return = os.popen(command_send).read()
        # LOG.debug(self.command_return)
        self.check_errors(command_return)

    @staticmethod
    def check_errors(command_return: str):
        """
            Check through error codes in i2cDump
        """

        # register 0x37
        fs_mon = command_return.splitlines()[4][25:27]
        fs_mon_str = ["FS Error", "", "", "", "", "", "32KHz", "", "Reserved",
                      "48KHz", "", "96KHz"]
        LOG.debug("FS_MON: %s   (reg: 0x37)" % fs_mon_str[int(fs_mon)])

        # (reg: 0x70)
        error_string = command_return.splitlines()[8][4:6]
        error_string_bin = "{0:08b}".format(int(error_string, 16))
        if error_string_bin[-4] == "1":
            LOG.debug("Left channel DC fault")
        if error_string_bin[-3] == "1":
            LOG.debug("Right channel DC fault")
        if error_string_bin[-2] == "1":
            LOG.debug("Left channel over current fault")
        if error_string_bin[-1] == "1":
            LOG.debug("Right channel over current fault")

        # (reg: 0x71)
        error_string = command_return.splitlines()[8][7:9]
        error_string_bin = "{0:08b}".format(int(error_string, 16))
        if error_string_bin[-3] == "1":
            LOG.debug("Clock fault (reg: 0x71)")

        # register 0x68
        run_status = command_return.splitlines()[7][29:31]
        run_status_str = ["Deep sleep", "Sleep", "HIZ", "Play"]
        LOG.debug("Run Status: %s   (reg: 0x68)" % run_status_str[int(run_status)])

    def write_data(self, addr, val, comment=""):
        self.bus.write_byte_data(self.devAddr, addr, val)
        LOG.debug(f"write: {hex(addr)}: {hex(val)} - {comment}")
        time.sleep(0.1)

    def close(self):
        self.bus.close()

    def start_sequence(self):
        """
            Start Sequence for the TAS5806
        """
        self.write_data(0x01, 0x11, "Reset Chip")
        self.write_data(0x78, 0x80, "Clear Faults")
        self.dump_data()
        self.write_data(0x01, 0x00, "Remove Reset")
        self.write_data(0x78, 0x00, "Remove Clear Fault")
        self.dump_data()

        self.write_data(0x33, 0x03, "32-bit")
        self.dump_data()
        self.set_volume(0x60)
        self.write_data(0x30, 0x01, "SDOUT is the DSP input (pre-processing)")

        self.write_data(0x03, 0x00, "Deep Sleep")
        self.dump_data()

        self.write_data(0x03, 0x02, "HiZ")
        self.dump_data()

        self.write_data(0x5C, 0x01, "coefficient")
        self.dump_data()
        self.write_data(0x03, 0x03, "Play")
        self.dump_data()

    def calc_log_y(self, x):
        """ given x produce y. takes in an int
        0-100 returns a log oriented hardware
        value with larger steps for low volumes
        and smaller steps for loud volumes """
        if x < 0:
            x = 0

        if x > 100:
            x = 100

        x0 = 0  # input range low
        x1 = 100  # input range hi

        y0 = self.MAX_VOL  # max hw vol
        y1 = 210  # min hw val

        p1 = (x - x0) / (x1 - x0)
        p2 = log(y0) - log(y1)
        pval = p1 * p2 + log(y1)

        return round(exp(pval))

    def calc_log_x(self, y):
        """ given y produce x. takes in an int
        30-210 returns a value from 0-100 """
        if y < 0:
            y = self.MAX_VOL

        if y > 210:
            y = 210

        x0 = 0  # input range low
        x1 = 100  # input range hi

        y0 = self.MAX_VOL  # max hw vol
        y1 = 210  # min hw val

        x = x1 - x0
        p1 = (log(y) - log(y0)) / (log(y1) - log(y0))

        return x * p1 + x0

    def set_volume(self, vol=1.0):
        # vol takes a float from 0.0 - 1.0
        # default vol 0.5 = 50%
        hw_vol = self.calc_log_y(vol * 100.0)
        set_vol_str = f"Set Volume {hw_vol}"
        self.write_data(0x4c, hw_vol, set_vol_str)


def init_tas5806():
    tt = Tas5806()
    tt.start_sequence()
    tt.set_volume()
    tt.close()
