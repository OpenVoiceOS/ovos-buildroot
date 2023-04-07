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

import sys
import os
import unittest
from copy import deepcopy
from threading import Event

from mycroft_bus_client import Message


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class UserUtilTests(unittest.TestCase):
    def test_get_user_prefs(self):
        from neon_utils.user_utils import get_user_prefs

        test_user_1_profile = {"user": {"username": "test_user_1",
                                        "email": "test@neon.ai"}}
        test_user_2_profile = {"user": {"username": "test_user_2",
                                        "address": "new_key"}}
        test_message_1 = Message("test_message", {}, {
            "username": "test_user_1",
            "user_profiles": [test_user_1_profile,
                              test_user_2_profile]})
        test_message_2 = Message("test_message", {}, {
            "username": "test_user_2",
            "user_profiles": [test_user_1_profile,
                              test_user_2_profile]})

        user_1 = get_user_prefs(test_message_1)
        self.assertEqual(user_1["user"]["username"], "test_user_1")
        self.assertEqual(user_1["user"]["email"], "test@neon.ai")
        self.assertEqual(test_message_1.context['user_profiles'][0], user_1)

        user_2 = get_user_prefs(test_message_2)
        self.assertEqual(user_2["user"]["username"], "test_user_2")
        self.assertIn("address", user_2["user"])
        self.assertEqual(test_message_2.context['user_profiles'][1], user_2)

        def wrapper(message, valid_dict):
            self.assertEqual(get_user_prefs(), valid_dict)

        wrapper(test_message_1, user_1)
        wrapper(test_message_2, user_2)

    def test_get_default_user_config_from_mycroft_conf(self):
        test_config_dir = os.path.join(os.path.dirname(__file__),
                                       "user_util_test_config")
        os.environ["NEON_CONFIG_PATH"] = test_config_dir
        os.environ["XDG_CONFIG_HOME"] = test_config_dir
        from neon_utils.user_utils import get_default_user_config
        user_config = get_default_user_config()
        self.assertFalse(os.path.isfile(os.path.join(test_config_dir,
                                                     "ngi_user_info.yml")))
        self.assertIsInstance(user_config, dict)
        self.assertEqual(user_config["location"],
                         {"lat": '38.971669',
                          "lng": '-95.23525',
                          "tz": 'America/Chicago',
                          "utc": '-6.0',
                          "city": 'Kirkland',
                          "state": 'Washington',
                          "country": "United States"})

        os.environ.pop("NEON_CONFIG_PATH")
        os.environ.pop("XDG_CONFIG_HOME")

    def test_update_user_profile(self):
        from neon_utils.user_utils import update_user_profile
        from ovos_utils.messagebus import FakeBus

        test_config_dir = os.path.join(os.path.dirname(__file__),
                                       "user_util_test_config")
        os.environ["NEON_CONFIG_PATH"] = test_config_dir
        os.environ["XDG_CONFIG_HOME"] = test_config_dir
        from neon_utils.user_utils import get_default_user_config
        user_config = get_default_user_config()
        user_config["user"]["username"] = "test_user"
        username = user_config["user"]["username"]
        self.assertIsInstance(user_config, dict)
        new_email = "developers@neon.ai"

        test_message = Message("test", {}, {"user_profiles": [user_config],
                                            "username": username})
        update_message = None
        updated = Event()
        bus = FakeBus()

        def _handle_update(message):
            nonlocal update_message
            update_message = message
            updated.set()
        bus.on("neon.profile_update", _handle_update)

        updated.clear()
        update_user_profile({"user": {"email": new_email}}, test_message, bus)
        self.assertEqual(
            test_message.context["user_profiles"][0]["user"]["email"],
            new_email)
        updated.wait(5)
        self.assertIsInstance(update_message, Message)
        self.assertEqual(test_message.context["user_profiles"][0],
                         update_message.data["profile"])
        self.assertEqual(update_message.data["profile"]["user"]["username"],
                         "test_user")

        valid_profile = deepcopy(update_message.data["profile"])
        updated.clear()
        update_user_profile({"invalid_key": {},
                             "user": {"invalid_key": "val"}},
                            test_message, bus)
        self.assertEqual(test_message.context["user_profiles"][0],
                         valid_profile)
        updated.wait(5)
        self.assertEqual(update_message.data["profile"], valid_profile)

    def test_apply_user_profile_updates(self):
        from neon_utils.user_utils import apply_local_user_profile_updates
        from neon_utils.configuration_utils import NGIConfig
        config_object = NGIConfig("test_config", os.path.dirname(__file__))
        config_object["test"] = {"updated": "",
                                 "unchanged": True
                                 }

        apply_local_user_profile_updates({"test": {"updated": "yes",
                                             "added": 1}}, config_object)
        self.assertEqual(dict(config_object.content),
                         {"test": {"updated": "yes",
                                   "unchanged": True,
                                   "added": 1}})
        self.assertFalse(config_object._pending_write)
        os.remove(os.path.join(config_object.path,
                               f".{config_object.name}.tmp"))
        os.remove(config_object.file_path)


if __name__ == '__main__':
    unittest.main()
