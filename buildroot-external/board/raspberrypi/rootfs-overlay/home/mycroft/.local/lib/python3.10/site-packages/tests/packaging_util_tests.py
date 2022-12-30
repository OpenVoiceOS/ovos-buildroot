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

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.packaging_utils import *


class PackagingUtilTests(unittest.TestCase):
    def test_get_neon_core_version(self):
        version = get_neon_core_version()
        self.assertIsInstance(version, str)
        self.assertGreaterEqual(len(version.split('.')), 2)

    def test_get_core_root(self):
        try:
            core_dir = get_core_root()
            self.assertIsInstance(core_dir, str)
            self.assertTrue(os.path.isdir(os.path.join(core_dir, "mycroft")))
        except FileNotFoundError:
            with self.assertRaises(FileNotFoundError):
                get_core_root()

    def test_get_neon_core_root(self):
        try:
            core_dir = get_neon_core_root()
            self.assertIsInstance(core_dir, str)
            self.assertTrue(os.path.isdir(os.path.join(core_dir, "util")))
        except FileNotFoundError:
            with self.assertRaises(FileNotFoundError):
                get_neon_core_root()

    def test_get_mycroft_core_root(self):
        try:
            core_dir = get_mycroft_core_root()
            self.assertIsInstance(core_dir, str)
            self.assertTrue(os.path.isdir(os.path.join(core_dir, "mycroft")))
        except FileNotFoundError:
            with self.assertRaises(FileNotFoundError):
                get_mycroft_core_root()

    def test_get_package_version_spec(self):
        ver = get_package_version_spec("ovos_utils")
        self.assertIsInstance(ver, str)

        with self.assertRaises(ModuleNotFoundError):
            get_package_version_spec("neon-stt-fake-test-package")

        with self.assertRaises(ModuleNotFoundError):
            get_package_version_spec("mycroft")

    def test_parse_version_string(self):
        major, minor, patch, alpha = parse_version_string("21.5")
        self.assertEqual(major, 21)
        self.assertEqual(minor, 5)
        self.assertEqual(patch, 0)
        self.assertEqual(alpha, None)

        major, minor, patch, alpha = parse_version_string("21.5.1")
        self.assertEqual(major, 21)
        self.assertEqual(minor, 5)
        self.assertEqual(patch, 1)
        self.assertEqual(alpha, None)

        major, minor, patch, alpha = parse_version_string("21.5.1a0")
        self.assertEqual(major, 21)
        self.assertEqual(minor, 5)
        self.assertEqual(patch, 1)
        self.assertEqual(alpha, 0)

        major, minor, patch, alpha = parse_version_string("21.5.2post2")
        self.assertEqual(major, 21)
        self.assertEqual(minor, 5)
        self.assertEqual(patch, 2)
        self.assertEqual(alpha, 2)

    def test_get_packaged_core_version(self):
        try:
            ver = get_packaged_core_version()
            self.assertIsInstance(ver, str)
            self.assertGreaterEqual(len(ver.split('.')), 2)
        except ImportError:
            with self.assertRaises(ImportError):
                get_packaged_core_version()

    def test_get_package_dependencies(self):
        self_deps = get_package_dependencies("neon-utils")
        requirements_file = join(os.path.dirname(os.path.dirname(__file__)),
                                 "requirements", "requirements.txt")
        with open(requirements_file) as f:
            spec_requirements = f.read().split('\n')
        spec_requirements = [r for r in spec_requirements if r]
        # Version specs aren't order-dependent, so they can't be compared
        self.assertEqual(len(self_deps), len(spec_requirements))
        with self.assertRaises(ModuleNotFoundError):
            get_package_dependencies("fakeneongeckopackage")

    def test_build_skill_spec(self):
        import json
        from neon_utils.packaging_utils import build_skill_spec
        test_dir = os.path.join(os.path.dirname(__file__), "test_skill_json")

        with self.assertRaises(FileNotFoundError):
            build_skill_spec(os.path.join(test_dir, "notADirectory"))
        with self.assertRaises(FileNotFoundError):
            build_skill_spec(__file__)

        skill_spec = build_skill_spec(test_dir)
        self.assertIsInstance(skill_spec, dict)
        # Patch params otherwise read from .git directory
        skill_spec["authorname"] = "NeonGeckoCom"
        skill_spec["skillname"] = "skill-alerts"
        skill_spec["url"] = "https://github.com/NeonGeckoCom/skill-alerts"
        with open(join(test_dir, "skill.json")) as f:
            valid_spec = json.load(f)
        self.assertEqual(valid_spec, skill_spec)

    # TODO: Actually validate exception cases? DM


if __name__ == '__main__':
    unittest.main()
