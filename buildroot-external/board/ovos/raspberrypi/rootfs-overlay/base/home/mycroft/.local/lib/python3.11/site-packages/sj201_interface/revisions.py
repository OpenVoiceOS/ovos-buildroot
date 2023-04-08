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

from enum import Enum
from subprocess import Popen, PIPE
from typing import Optional


class SJ201(Enum):
    r6 = "6"
    r10 = "10"


def detect_sj201_revision() -> Optional[SJ201]:
    """
    Detect which revision of SJ201 (if any) is connected.
    """
    tiny_address = "04"
    xmos_address = "2c"
    ti_address = "2f"
    cmd = "i2cdetect -a -y 1 | grep %s" % (tiny_address,)
    process = Popen(cmd, stdout=PIPE, stderr=None, shell=True)
    tiny_is_present = True if process.communicate()[0] else False

    cmd = "i2cdetect -a -y 1 | grep %s" % (xmos_address,)
    process = Popen(cmd, stdout=PIPE, stderr=None, shell=True)
    xmos_is_present = True if process.communicate()[0] else False

    cmd = "i2cdetect -a -y 1 | grep %s" % (ti_address,)
    process = Popen(cmd, stdout=PIPE, stderr=None, shell=True)
    ti_is_present = True if process.communicate()[0] else False

    if ti_is_present and xmos_is_present:
        if tiny_is_present:
            return SJ201.r6
        else:
            return SJ201.r10
    return None
