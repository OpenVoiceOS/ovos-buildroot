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

import unittest
import sys
import os

from ovos_utils.messagebus import FakeBus

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.validator_utils import *


class ValidatorUtilTests(unittest.TestCase):
    def test_numeric_confirmation_validator_valid(self):
        validator = numeric_confirmation_validator("123")
        self.assertTrue(validator("123"))
        self.assertTrue(validator("1 2 3."))
        self.assertTrue(validator("one two three"))
        self.assertTrue(validator("one hundred twenty three"))
        self.assertTrue(validator("blah blah one two three nah"))

        self.assertFalse(validator("one thousand two hundred and three"))
        self.assertFalse(validator("123 4"))

    def test_numeric_confirmation_validator_type_error(self):
        with self.assertRaises(TypeError):
            numeric_confirmation_validator(123)

        with self.assertRaises(ValueError):
            numeric_confirmation_validator("one two three")

        with self.assertRaises(ValueError):
            numeric_confirmation_validator("")

    def test_string_confirmation_validator_valid(self):
        validator = string_confirmation_validator("test phrase")
        self.assertTrue(validator("test phrase"))
        self.assertTrue(validator("yes test phrase yes"))

        self.assertFalse(validator("test no phrase"))
        self.assertFalse(validator("phrase test"))

    def test_string_confirmation_validator_type_error(self):
        with self.assertRaises(TypeError):
            string_confirmation_validator(123)

        with self.assertRaises(ValueError):
            string_confirmation_validator("")

    def test_voc_confirmation_validator_valid(self):
        sys.path.append(os.path.dirname(__file__))
        from valid_skill import ValidNeonSkill
        skill = ValidNeonSkill()
        if hasattr(skill, "_startup"):
            skill._startup(FakeBus())
        validator = voc_confirmation_validator("test", ValidNeonSkill())
        self.assertTrue(validator("test"))
        self.assertTrue(validator("something"))

        self.assertFalse(validator("else"))
        self.assertFalse(validator("false"))

    def test_voc_confirmation_validator_type_error(self):
        sys.path.append(os.path.dirname(__file__))
        from valid_skill import ValidNeonSkill
        skill = ValidNeonSkill()
        with self.assertRaises(TypeError):
            voc_confirmation_validator(123, skill)

        with self.assertRaises(FileNotFoundError):
            voc_confirmation_validator("invalid", skill)


if __name__ == '__main__':
    unittest.main()
