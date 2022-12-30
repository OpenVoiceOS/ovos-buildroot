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
import importlib
import shutil
import sys
import os
import unittest
import json
import yaml
import mock

from copy import deepcopy
from time import sleep
from glob import glob
from os.path import join, dirname, isdir, basename, isfile, expanduser, \
    getmtime

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.log_utils import LOG

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, "configuration")

TEST_DICT = {"section 1": {"key1": "val1",
                           "key2": "val2"},
             "section 2": {"key_1": "val1",
                           "key_2": "val2"}}


class NGIConfigTests(unittest.TestCase):
    def doCleanups(self) -> None:
        if os.getenv("NEON_CONFIG_PATH"):
            os.environ.pop("NEON_CONFIG_PATH")
        for file in glob(os.path.join(CONFIG_PATH, ".*.lock")):
            os.remove(file)
        for file in glob(os.path.join(CONFIG_PATH, ".*.tmp")):
            os.remove(file)
        for file in glob(os.path.join(ROOT_DIR, "credentials", ".*.lock")):
            os.remove(file)
        for file in glob(os.path.join(ROOT_DIR, "credentials", ".*.tmp")):
            os.remove(file)
        if os.path.exists(os.path.join(CONFIG_PATH, "old_user_info.yml")):
            os.remove(os.path.join(CONFIG_PATH, "old_user_info.yml"))

    def test_load_config(self):
        from neon_utils.configuration_utils import NGIConfig
        local_conf = NGIConfig("ngi_local_conf", CONFIG_PATH)
        self.assertIsInstance(local_conf.content, dict)
        self.assertIsInstance(local_conf.content["devVars"], dict)
        self.assertIsInstance(local_conf.content["prefFlags"]["devMode"], bool)

    def test_config_get(self):
        from neon_utils.configuration_utils import NGIConfig
        local_conf = NGIConfig("ngi_local_conf", CONFIG_PATH)
        self.assertIsInstance(local_conf, NGIConfig)
        self.assertIsInstance(local_conf.content, dict)
        self.assertIsInstance(local_conf["devVars"], dict)
        self.assertIsInstance(local_conf["prefFlags"]["devMode"], bool)
        self.assertEqual(local_conf["prefFlags"], local_conf.get("prefFlags"))
        self.assertIsNone(local_conf.get("fake_key"))
        self.assertTrue(local_conf.get("fake_key", True))

    def test_config_set(self):
        from neon_utils.configuration_utils import NGIConfig
        local_conf = NGIConfig("ngi_local_conf", CONFIG_PATH)
        self.assertIsInstance(local_conf.content, dict)
        self.assertIsInstance(local_conf["prefFlags"]["devMode"], bool)

        local_conf["prefFlags"]["devMode"] = True
        self.assertTrue(local_conf["prefFlags"]["devMode"])

        local_conf["prefFlags"]["devMode"] = False
        self.assertFalse(local_conf["prefFlags"]["devMode"])

    def test_get_config_dir_invalid_override(self):
        from neon_utils.configuration_utils import get_config_dir
        os.environ["NEON_CONFIG_PATH"] = "/invalid"
        config_path = get_config_dir()
        self.assertNotEqual(config_path, "/invalid")
        os.environ.pop("NEON_CONFIG_PATH")
        self.assertIsNone(os.getenv("NEON_CONFIG_PATH"))

    def test_make_equal_keys(self):
        from neon_utils.configuration_utils import NGIConfig
        old_user_info = os.path.join(CONFIG_PATH, "old_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        shutil.copy(ngi_user_info, old_user_info)
        user_conf = NGIConfig("ngi_user_info", CONFIG_PATH, True)
        self.assertEqual(user_conf.content["user"]["full_name"], 'Test User')
        self.assertNotIn("phone_verified", user_conf.content["user"])
        self.assertIn('bad_key', user_conf.content["user"])

        user_conf.make_equal_by_keys(NGIConfig("clean_user_info",
                                               CONFIG_PATH).content)
        self.assertIn("phone_verified", user_conf.content["user"])
        self.assertNotIn('bad_key', user_conf.content["user"])
        self.assertFalse(user_conf.content["user"]["phone_verified"])
        self.assertEqual(user_conf.content["user"]["full_name"], 'Test User')

        new_user_info = NGIConfig("ngi_user_info", CONFIG_PATH)
        self.assertEqual(user_conf.content, new_user_info.content)
        shutil.copy(old_user_info, ngi_user_info)

    def test_make_equal_keys_no_recurse(self):
        from neon_utils.configuration_utils import NGIConfig
        skill_settings = NGIConfig("skill_populated", CONFIG_PATH)
        correct_settings = deepcopy(skill_settings.content)
        skill_settings.make_equal_by_keys(NGIConfig("skill_default",
                                                    CONFIG_PATH).content,
                                          False)
        self.assertEqual(correct_settings, skill_settings.content)

    def test_update_keys(self):
        from neon_utils.configuration_utils import NGIConfig
        old_user_info = os.path.join(CONFIG_PATH, "old_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        shutil.copy(ngi_user_info, old_user_info)
        user_conf = NGIConfig("ngi_user_info", CONFIG_PATH, True)
        self.assertEqual(user_conf.content["user"]["full_name"], 'Test User')
        self.assertNotIn("phone_verified", user_conf.content["user"])
        self.assertIn('bad_key', user_conf.content["user"])

        user_conf.update_keys(NGIConfig("clean_user_info",
                                        CONFIG_PATH).content)
        self.assertIn("phone_verified", user_conf.content["user"])
        self.assertIn('bad_key', user_conf.content["user"])
        self.assertFalse(user_conf.content["user"]["phone_verified"])
        self.assertEqual(user_conf.content["user"]["full_name"], 'Test User')

        new_user_info = NGIConfig("ngi_user_info", CONFIG_PATH)
        self.assertEqual(user_conf.content, new_user_info.content)
        shutil.move(old_user_info, ngi_user_info)

    def test_update_key(self):
        from neon_utils.configuration_utils import NGIConfig
        old_user_info = os.path.join(CONFIG_PATH, "old_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        shutil.copy(ngi_user_info, old_user_info)
        user_conf = NGIConfig("ngi_user_info", CONFIG_PATH)

        self.assertEqual(user_conf.content["user"]["full_name"], 'Test User')
        user_conf.update_yaml_file("user", "full_name", "New Name",
                                   multiple=False, final=True)
        self.assertEqual(user_conf.content["user"]["full_name"], 'New Name')
        new_user_conf = NGIConfig("ngi_user_info", CONFIG_PATH)
        self.assertEqual(user_conf.content["user"]["full_name"],
                         new_user_conf.content["user"]["full_name"])
        shutil.copy(old_user_info, ngi_user_info)

    def test_export_json(self):
        import json
        from neon_utils.configuration_utils import NGIConfig
        user_conf = NGIConfig("ngi_user_info", CONFIG_PATH)
        json_file = user_conf.export_to_json()
        with open(json_file, "r") as f:
            from_disk = json.load(f)
        self.assertEqual(from_disk, user_conf.content)
        os.remove(json_file)

    def test_import_dict(self):
        from neon_utils.configuration_utils import NGIConfig
        test_conf = NGIConfig("test_conf", CONFIG_PATH).from_dict(TEST_DICT)
        self.assertEqual(test_conf.content, TEST_DICT)
        from_disk = NGIConfig("test_conf", CONFIG_PATH)
        self.assertEqual(from_disk.content, test_conf.content)
        os.remove(test_conf.file_path)

    def test_import_json(self):
        from neon_utils.configuration_utils import NGIConfig
        from ovos_utils.json_helper import load_commented_json
        json_path = os.path.join(CONFIG_PATH, "mycroft.conf")
        test_conf = NGIConfig("mycroft", CONFIG_PATH).from_json(json_path)
        parsed_json = load_commented_json(json_path)
        self.assertEqual(parsed_json, test_conf.content)
        from_disk = NGIConfig("mycroft", CONFIG_PATH)
        self.assertEqual(from_disk.content, test_conf.content)
        os.remove(test_conf.file_path)

    def test_config_cache(self):
        from neon_utils.configuration_utils import NGIConfig
        from neon_utils.configuration_utils import NGIConfig as NGIConf2
        bak_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.bak")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")

        shutil.copy(ngi_local_conf, bak_local_conf)
        config_1 = NGIConfig("ngi_local_conf", CONFIG_PATH)
        self.assertFalse(config_1.requires_reload)
        config_2 = NGIConf2("ngi_local_conf", CONFIG_PATH, True)
        self.assertFalse(config_2.requires_reload)
        self.assertEqual(config_1._content, config_2._content)
        self.assertNotEqual(config_1, config_2)

        config_1.update_yaml_file("prefFlags", "autoStart", False)
        self.assertFalse(config_1._pending_write)
        self.assertEqual(config_2._content["prefFlags"]["autoStart"], True)
        self.assertFalse(config_2._pending_write)

        self.assertNotEqual(config_1._loaded, config_2._loaded)
        self.assertGreater(config_1._loaded, config_2._loaded)
        self.assertTrue(config_2.requires_reload)
        self.assertEqual(config_1.content, config_2.content)
        self.assertEqual(config_1._loaded, config_2._loaded)

        config_2.update_yaml_file("prefFlags", "devMode", False, multiple=True)
        self.assertFalse(config_2["prefFlags"]["devMode"])
        self.assertTrue(config_2._pending_write)
        config_2.write_changes()
        self.assertFalse(config_2._pending_write)
        self.assertTrue(config_1.requires_reload)
        self.assertEqual(config_1.content["prefFlags"]["devMode"], False)

        config_2.update_yaml_file("prefFlags", "devMode", True, multiple=True)
        self.assertTrue(config_2._pending_write)
        self.assertTrue(config_2["prefFlags"]["devMode"])
        self.assertFalse(config_1["prefFlags"]["devMode"])

        shutil.move(bak_local_conf, ngi_local_conf)

    def test_multi_config(self):
        from neon_utils.configuration_utils import NGIConfig
        bak_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.bak")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")

        shutil.copy(ngi_local_conf, bak_local_conf)

        config_objects = []
        for i in range(100):
            config_objects.append(NGIConfig("ngi_local_conf",
                                            CONFIG_PATH, True))

        first_config = config_objects[0]
        last_config = config_objects[-1]
        self.assertIsInstance(first_config, NGIConfig)
        self.assertIsInstance(last_config, NGIConfig)

        self.assertEqual(first_config.content, last_config.content)
        first_config.update_yaml_file("prefFlags", "devMode", False)

        self.assertFalse(last_config["prefFlags"]["devMode"])
        self.assertEqual(first_config.content, last_config.content)

        shutil.move(bak_local_conf, ngi_local_conf)

    def test_concurrent_config_read(self):
        from neon_utils.configuration_utils import NGIConfig
        from threading import Thread
        valid_config = NGIConfig("dep_user_info", CONFIG_PATH)
        test_results = {}

        def _open_config(idx):
            from neon_utils.configuration_utils import NGIConfig as Config
            config = Config("dep_user_info", CONFIG_PATH, True)
            test_results[idx] = config.content == valid_config.content

        for i in range(10):
            Thread(target=_open_config, args=(i,), daemon=True).start()
        while not len(test_results.keys()) == 10:
            sleep(0.5)
        self.assertTrue(all(test_results.values()))

    def test_new_ngi_config(self):
        from neon_utils.configuration_utils import NGIConfig
        config = NGIConfig("temp_conf", CONFIG_PATH)
        self.assertIsInstance(config.content, dict)
        os.remove(os.path.join(CONFIG_PATH, "temp_conf.yml"))


class ConfigurationUtilTests(unittest.TestCase):
    def doCleanups(self) -> None:
        if os.getenv("NEON_CONFIG_PATH"):
            os.environ.pop("NEON_CONFIG_PATH")
        for file in glob(os.path.join(CONFIG_PATH, ".*.lock")):
            os.remove(file)
        for file in glob(os.path.join(CONFIG_PATH, ".*.tmp")):
            os.remove(file)
        for file in glob(os.path.join(ROOT_DIR, "credentials", ".*.lock")):
            os.remove(file)
        for file in glob(os.path.join(ROOT_DIR, "credentials", ".*.tmp")):
            os.remove(file)
        if os.path.exists(os.path.join(CONFIG_PATH, "old_user_info.yml")):
            os.remove(os.path.join(CONFIG_PATH, "old_user_info.yml"))

    def test_get_legacy_config_path(self):
        from neon_utils.configuration_utils import _get_legacy_config_dir
        test_dir = join(CONFIG_PATH, "config_path_test_dirs")

        venv_path = join(test_dir, "arbitrary_venv")
        mycroft_path = join(test_dir, "default_mycroft")
        cloned_neon_path = join(test_dir, "cloned_neon")
        legacy_neon_path = join(test_dir, "legacy_neon_path")

        test_path = ["/lib/python3.8", "/usr/lib/python3.8", "/opt/mycroft"]
        self.assertIsNone(_get_legacy_config_dir(test_path))

        test_path.insert(0, f"{venv_path}/.venv/lib/python3.8/site-packages")
        self.assertEqual(_get_legacy_config_dir(test_path), venv_path)

        test_path.insert(0, mycroft_path)
        self.assertEqual(_get_legacy_config_dir(test_path), mycroft_path)

        test_path.insert(0, cloned_neon_path)
        self.assertEqual(_get_legacy_config_dir(test_path), cloned_neon_path)

        test_path.insert(0, legacy_neon_path)
        self.assertEqual(_get_legacy_config_dir(test_path),
                         f"{legacy_neon_path}/NGI")

        dev_test_path = ['', '/usr/lib/python38.zip', '/usr/lib/python3.8',
                         '/usr/lib/python3.8/lib-dynload',
                         f'{join(test_dir, "dev_environment")}/venv/lib/'
                         f'python3.8/site-packages',
                         f'{join(test_dir, "dev_environment")}/neon_cli',
                         f'{join(test_dir, "dev_environment")}/'
                         f'transcripts_controller',
                         f'{join(test_dir, "dev_environment")}/neon_enclosure',
                         f'{join(test_dir, "dev_environment")}/neon_speech',
                         f'{join(test_dir, "dev_environment")}/neon_audio',
                         f'{join(test_dir, "dev_environment")}/NeonCore',
                         f'{join(test_dir, "dev_environment")}/'
                         f'neon-test-utils',
                         f'{join(test_dir, "dev_environment")}/neon_display',
                         f'{join(test_dir, "dev_environment")}/'
                         f'neon_messagebus',
                         f'{join(test_dir, "dev_environment")}/neon_gui']
        self.assertEqual(_get_legacy_config_dir(dev_test_path),
                         f'{join(test_dir, "dev_environment")}/NeonCore')

    def test_get_config_dir(self):
        from neon_utils.configuration_utils import get_config_dir
        # default
        config_path = get_config_dir()
        self.assertTrue(os.path.isdir(config_path))

        # Valid override
        os.environ["XDG_CONFIG_HOME"] = expanduser("~/")
        config_path = get_config_dir()
        self.assertEqual(config_path, expanduser("~/neon"))
        self.assertTrue(os.path.isdir(config_path))
        os.environ.pop("XDG_CONFIG_HOME")
        self.assertIsNone(os.getenv("XDG_CONFIG_HOME"))

    def test_delete_recursive_dictionary_keys(self):
        from neon_utils.configuration_utils import \
            delete_recursive_dictionary_keys

        # Delete Key
        test_dict = deepcopy(TEST_DICT)
        test_dict = delete_recursive_dictionary_keys(test_dict, ["key_1",
                                                                 "key1"])
        self.assertEqual(test_dict, {"section 1": {"key2": "val2"},
                                     "section 2": {"key_2": "val2"}})

        # Delete Section
        test_dict = deepcopy(TEST_DICT)
        test_dict = delete_recursive_dictionary_keys(test_dict, ["section 1"])
        self.assertEqual(test_dict, {"section 2": {"key_1": "val1",
                                                   "key_2": "val2"}})

    def test_dict_merge(self):
        from neon_utils.configuration_utils import dict_merge
        to_update = deepcopy(TEST_DICT)
        new_keys = {"section 2": {"key_2": "new2",
                                  "key_3": "val3"}}
        updated = dict_merge(to_update, new_keys)
        self.assertEqual(updated["section 2"], {"key_1": "val1",
                                                "key_2": "new2",
                                                "key_3": "val3"})

    def test_dict_make_equal_keys(self):
        from neon_utils.configuration_utils import dict_make_equal_keys

        # Simple
        to_update = deepcopy(TEST_DICT)
        new_keys = {"section 2": {"key_2": "new2",
                                  "key_3": "val3"}}
        updated = dict_make_equal_keys(to_update, new_keys)
        self.assertEqual(updated, {"section 2": {"key_2": "val2",
                                                 "key_3": "val3"}
                                   })
        # Depth 0 (top level only)
        to_update = deepcopy(TEST_DICT)
        new_keys = {"section 2": {"key_2": "new2",
                                  "key_3": "val3"}}
        updated = dict_make_equal_keys(to_update, new_keys, 0)
        self.assertEqual(updated, {"section 2": {"key_1": "val1",
                                                 "key_2": "val2"}
                                   })

        # Depth 1
        to_update = deepcopy(TEST_DICT)
        to_update["section 2"]["key_2"] = {"2_data": "value"}
        new_keys = {"section 2": {"key_2": {},
                                  "key_3": "val3"}}
        updated = dict_make_equal_keys(to_update, new_keys, 1)
        self.assertEqual(updated, {"section 2": {"key_2": {"2_data": "value"},
                                                 "key_3": "val3"}
                                   })

        # Empty dict (invalid request)
        to_update = deepcopy(TEST_DICT)
        new_keys = dict()
        with self.assertRaises(ValueError):
            dict_make_equal_keys(to_update, new_keys)

    def test_dict_update_keys(self):
        from neon_utils.configuration_utils import dict_update_keys
        to_update = deepcopy(TEST_DICT)
        new_keys = {"section 2": {"key_2": "new2",
                                  "key_3": "val3"}}
        updated = dict_update_keys(to_update, new_keys)
        self.assertEqual(updated["section 2"], {"key_1": "val1",
                                                "key_2": "val2",
                                                "key_3": "val3"})

    def test_write_json(self):
        from neon_utils.configuration_utils import write_to_json
        file_path = os.path.join(CONFIG_PATH, "test.json")
        write_to_json(TEST_DICT, file_path)
        with open(file_path, "r") as f:
            from_disk = json.load(f)
        self.assertEqual(from_disk, TEST_DICT)
        os.remove(file_path)

    def test_get_user_config_add_keys(self):
        from neon_utils.configuration_utils import get_neon_user_config
        old_user_info = os.path.join(CONFIG_PATH, "old_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        bak_local_conf = os.path.join(CONFIG_PATH, "bak_local_conf.yml")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")

        shutil.copy(ngi_local_conf, bak_local_conf)
        shutil.copy(ngi_user_info, old_user_info)
        config = get_neon_user_config(CONFIG_PATH)
        user_config_keys = ["user", "brands", "speech", "units", "location"]
        self.assertTrue(all(k for k in user_config_keys if k in config))
        shutil.move(old_user_info, ngi_user_info)
        shutil.move(bak_local_conf, ngi_local_conf)

    def test_get_user_config_create(self):
        from neon_utils.configuration_utils import get_neon_user_config
        old_user_info = os.path.join(CONFIG_PATH, "old_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        bak_local_conf = os.path.join(CONFIG_PATH, "bak_local_conf.yml")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")

        shutil.copy(ngi_local_conf, bak_local_conf)
        shutil.move(ngi_user_info, old_user_info)
        config = get_neon_user_config(CONFIG_PATH)
        self.assertTrue(os.path.isfile(ngi_user_info))
        user_config_keys = ["user", "brands", "speech", "units", "location"]
        self.assertTrue(all(k for k in user_config_keys if k in config))
        shutil.move(old_user_info, ngi_user_info)
        shutil.move(bak_local_conf, ngi_local_conf)

    def test_get_user_config_migrate_keys(self):
        from neon_utils.configuration_utils import get_neon_user_config, \
            NGIConfig
        bak_user_info = os.path.join(CONFIG_PATH, "bak_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        old_user_info = os.path.join(CONFIG_PATH, "dep_user_info.yml")
        bak_local_conf = os.path.join(CONFIG_PATH, "bak_local_conf.yml")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")
        shutil.move(ngi_user_info, bak_user_info)
        shutil.copy(old_user_info, ngi_user_info)
        shutil.copy(ngi_local_conf, bak_local_conf)

        user_conf = get_neon_user_config(CONFIG_PATH)
        user_config_keys = ["user", "brands", "speech", "units", "location"]
        self.assertTrue(all(k for k in user_config_keys if k in user_conf))

        local_config_keys = ["speech", "interface", "listener", "skills",
                             "session", "tts", "stt", "logs", "device"]
        local_conf = NGIConfig("ngi_local_conf", CONFIG_PATH)
        self.assertTrue(all(k for k in local_config_keys if k in local_conf))

        shutil.move(bak_user_info, ngi_user_info)
        shutil.move(bak_local_conf, ngi_local_conf)

    def test_user_config_keep_keys(self):
        from neon_utils.configuration_utils import get_neon_user_config
        bak_user_info = os.path.join(CONFIG_PATH, "bak_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        shutil.move(ngi_user_info, bak_user_info)

        user_conf = get_neon_user_config(CONFIG_PATH)
        user_conf.update_yaml_file("brands", "favorite_brands", {'neon': 1})
        self.assertEqual(user_conf["brands"]["favorite_brands"]['neon'], 1)

        new_user_conf = get_neon_user_config(CONFIG_PATH)
        self.assertEqual(user_conf.content, new_user_conf.content)
        self.assertEqual(user_conf["brands"]["favorite_brands"]['neon'], 1)

        shutil.move(bak_user_info, ngi_user_info)

    def test_get_mycroft_compat_config(self):
        from neon_utils.configuration_utils import \
            get_mycroft_compatible_config
        mycroft_config = get_mycroft_compatible_config()
        self.assertIsInstance(mycroft_config, dict)
        self.assertIsInstance(mycroft_config["gui_websocket"], dict)
        self.assertIsInstance(mycroft_config["gui_websocket"]["host"], str)
        self.assertIsInstance(mycroft_config["gui_websocket"]["base_port"],
                              int)
        self.assertIsInstance(mycroft_config["ready_settings"], list)
        self.assertIsInstance(mycroft_config['tts'], dict)
        self.assertIsInstance(mycroft_config["keys"], dict)
        # self.assertEqual(mycroft_config["skills"]["directory"],
        #                  mycroft_config["skills"]["directory_override"])
        self.assertIsInstance(mycroft_config["language"], dict)
        self.assertIsInstance(mycroft_config["listener"], dict)
        self.assertIsInstance(mycroft_config["stt"], dict)
        self.assertIsInstance(mycroft_config["tts"], dict)
        try:
            from typing import OrderedDict
            self.assertNotIsInstance(mycroft_config['tts'], OrderedDict)
            # self.assertNotIsInstance(mycroft_config['tts']['amazon'],
            #                          OrderedDict)
        except ImportError:
            pass

    def test_make_loaded_config_safe(self):
        from ruamel.yaml import YAML
        from neon_utils.configuration_utils import _make_loaded_config_safe
        test_config = join(dirname(__file__), "configuration",
                           "local_conf_with_stt_tts.yml")
        with open(test_config) as f:
            config = YAML().load(f)
        clean_config = _make_loaded_config_safe(config)
        self.assertIsInstance(clean_config, dict)
        try:
            from typing import OrderedDict
            self.assertNotIsInstance(clean_config['tts'], OrderedDict)
            self.assertNotIsInstance(clean_config['tts']['amazon'],
                                     OrderedDict)
        except ImportError:
            pass

    def test_is_neon_core(self):
        from neon_utils.configuration_utils import is_neon_core
        self.assertIsInstance(is_neon_core(), bool)

    def test_create_config_from_setup_params(self):
        from neon_utils.configuration_utils import \
            create_config_from_setup_params
        # devMode
        test_dir = f"{ROOT_DIR}/test_setup_config"
        os.environ["devMode"] = "true"
        os.environ["autoStart"] = "true"
        os.environ["autoUpdate"] = "false"
        os.environ["devName"] = "Test-Device"
        os.environ["sttModule"] = "stt_module"
        os.environ["ttsModule"] = "tts_module"
        os.environ["installServer"] = "false"
        os.environ["installerDir"] = test_dir
        os.environ["logsDir"] = test_dir
        os.environ["GITHUB_TOKEN"] = "git_token"
        config = create_config_from_setup_params(test_dir)

        self.assertTrue(config["debug"])
        self.assertFalse(config["skills"]["auto_update"])
        self.assertEqual(config["device_name"], "Test-Device")
        self.assertEqual(config["stt"]["module"], "stt_module")
        self.assertEqual(config["tts"]["module"], "tts_module")
        self.assertEqual(config["log_dir"], test_dir)
        with open(join(test_dir, "neon.yaml")) as f:
            disk_config = yaml.safe_load(f)
        self.assertEqual(config, disk_config)
        shutil.rmtree(test_dir)

    def test_write_mycroft_compatible_config(self):
        from neon_utils.configuration_utils import \
            get_mycroft_compatible_config, write_mycroft_compatible_config
        test_path = os.path.join(CONFIG_PATH, "test.conf")
        config = get_mycroft_compatible_config()
        write_mycroft_compatible_config(test_path)
        with open(test_path) as f:
            from_disk = json.load(f)
        self.assertEqual(from_disk, config)
        write_mycroft_compatible_config(test_path)
        with open(test_path) as f:
            from_disk_2 = json.load(f)
        self.assertEqual(from_disk_2, config)
        self.assertIsNone(config["Audio"].get("Audio"))
        os.remove(test_path)

    def test_config_no_permissions(self):
        from neon_utils.configuration_utils import NGIConfig
        with self.assertRaises(PermissionError):
            NGIConfig("test_config", "/root/")

    def test_parse_skill_configuration_valid(self):
        from neon_utils.configuration_utils import parse_skill_default_settings
        with open(join(CONFIG_PATH, "skill_settingsmeta.json")) as f:
            default_settings = json.load(f)
        parsed_settings = parse_skill_default_settings(default_settings)
        self.assertIsInstance(parsed_settings, dict)

    def test_populate_read_only_config_simple(self):
        from neon_utils.configuration_utils import NGIConfig
        from neon_utils.configuration_utils import _populate_read_only_config
        test_dir = os.path.join(ROOT_DIR, "configuration", "populate_tests")
        ro_dir = os.path.join(test_dir, "test_ro_dir")
        test_conf = NGIConfig("ngi_local_conf", test_dir, True)
        test_filename = basename(test_conf.file_path)

        self.assertTrue(_populate_read_only_config(ro_dir,
                                                   test_filename, test_conf))
        os.remove(test_conf.file_path)

    @mock.patch('neon_utils.configuration_utils._init_ovos_conf')
    def test_init_config_dir(self, init_ovos_conf):
        from neon_utils.configuration_utils import init_config_dir
        ro_dir = os.path.join(ROOT_DIR, "configuration", "unwritable_path")
        config_dir = os.path.join(ROOT_DIR, "configuration", "test")
        os.environ["NEON_CONFIG_PATH"] = ro_dir
        os.environ["XDG_CONFIG_HOME"] = config_dir
        init_config_dir()

        # Test config migration
        self.assertEqual(os.environ["NEON_CONFIG_PATH"],
                         join(config_dir, "neon"))
        self.assertFalse(os.path.exists(join(config_dir, "neon",
                                             "ngi_local_conf.yml")))
        self.assertTrue(os.path.exists(join(config_dir, "neon",
                                            "ngi_local_conf.bak")))
        self.assertTrue(os.path.exists(join(config_dir, "neon",
                                            "neon.yaml")))
        with open(join(config_dir, "neon", "neon.yaml")) as f:
            config = yaml.safe_load(f)
        with open(join(config_dir, "neon", "ngi_local_conf.bak")) as f:
            old_config = yaml.safe_load(f)
        self.assertEqual(config["MQ"], old_config["MQ"])

        init_ovos_conf.assert_called_once()
        shutil.rmtree(os.environ.pop("XDG_CONFIG_HOME"))
        os.environ.pop("NEON_CONFIG_PATH")

    def test_get_mycroft_compatible_location(self):
        from neon_utils.configuration_utils import \
            get_mycroft_compatible_location, get_neon_user_config

        old_user_info = os.path.join(CONFIG_PATH, "old_user_info.yml")
        ngi_user_info = os.path.join(CONFIG_PATH, "ngi_user_info.yml")
        shutil.copy(ngi_user_info, old_user_info)

        user_config = get_neon_user_config(CONFIG_PATH)

        with self.assertRaises(KeyError):
            get_mycroft_compatible_location(user_config.content)

        # Default mycroft.conf
        location = get_mycroft_compatible_location(user_config["location"])

        self.assertIsInstance(location["city"]["name"], str)
        self.assertIsInstance(location["city"]["code"], str)
        self.assertIsInstance(location["city"]["state"]["name"], str)
        self.assertIsInstance(location["city"]["state"]["code"], str)
        self.assertIsInstance(location["city"]["state"]["country"]["name"], str)
        self.assertIsInstance(location["city"]["state"]["country"]["code"], str)

        self.assertIsInstance(location["timezone"]["code"], str)
        self.assertIsInstance(location["coordinate"]["latitude"], float)
        self.assertIsInstance(location["coordinate"]["longitude"], float)
        self.assertIsInstance(location["timezone"]["name"], str)
        self.assertIsInstance(location["timezone"]["offset"], (float, int))
        self.assertEqual(location["timezone"]["dstOffset"], 3600000)

        # Valid user configured location
        user_config['location'] = {
            'lat': '47.4799078',
            'lng': '-122.2034496',
            'city': 'Renton',
            'state': 'Washington',
            'country': 'United States',
            'tz': 'America/Los_Angeles',
            'utc': '-8.0'
        }
        location = get_mycroft_compatible_location(user_config["location"])
        self.assertEqual(location["city"]["name"],
                         user_config["location"]["city"])
        self.assertEqual(location["city"]["code"],
                         user_config["location"]["city"])
        self.assertEqual(location["city"]["state"]["name"],
                         user_config["location"]["state"])
        self.assertIsInstance(location["city"]["state"]["code"], str)
        self.assertEqual(location["city"]["state"]["country"]["name"],
                         user_config["location"]["country"])
        self.assertEqual(location["city"]["state"]["country"]["code"], "us")

        self.assertIsInstance(location["coordinate"]["latitude"], float)
        self.assertEqual(str(location["coordinate"]["latitude"]),
                         user_config["location"]["lat"])
        self.assertIsInstance(location["coordinate"]["longitude"], float)
        self.assertEqual(str(location["coordinate"]["longitude"]),
                         user_config["location"]["lng"])

        self.assertEqual(location["timezone"]["code"],
                         user_config["location"]["tz"])
        self.assertIsInstance(location["timezone"]["name"], str)
        self.assertIsInstance(location["timezone"]["offset"], float)
        self.assertEqual(location["timezone"]["dstOffset"], 3600000)

        real_lat = user_config["location"]["lat"]
        real_lon = user_config["location"]["lng"]

        # Quoted strings in location
        user_config["location"]["lat"] = f'"{real_lat}"'
        user_config["location"]["lng"] = f'"{real_lon}"'
        user_config["location"]["utc"] = '-8.0'
        location = get_mycroft_compatible_location(user_config["location"])
        self.assertEqual(location["city"]["state"]["country"]["name"],
                         user_config["location"]["country"])
        self.assertEqual(location["coordinate"]["latitude"], float(real_lat))
        self.assertEqual(location["coordinate"]["longitude"], float(real_lon))
        self.assertEqual(location["city"]["state"]["country"]["code"], "us")

        self.assertIsInstance(location["coordinate"]["latitude"], float)
        self.assertIsInstance(location["coordinate"]["longitude"], float)
        self.assertIsInstance(location["timezone"]["offset"], float)

        user_config["location"]["lat"] = f"'{real_lat}'"
        user_config["location"]["lng"] = f"'{real_lon}'"
        location = get_mycroft_compatible_location(user_config["location"])
        self.assertIsInstance(location["coordinate"]["latitude"], float)
        self.assertIsInstance(location["coordinate"]["longitude"], float)
        user_config["location"]["utc"] = '"-8.0"'
        location = get_mycroft_compatible_location(user_config["location"])
        self.assertIsInstance(location["timezone"]["offset"], float)

        # Float
        user_config["location"]["utc"] = 8.0
        location = get_mycroft_compatible_location(user_config["location"])
        self.assertIsInstance(location["timezone"]["offset"], float)

        user_config["location"]["utc"] = ''
        location = get_mycroft_compatible_location(user_config["location"])
        self.assertIsInstance(location["timezone"]["offset"], float)

        # Incomplete user locations
        location = {
            'lat': None,
            'lng': None,
            'city': None,
            'state': None,
            'country': None,
            'tz': None,
            'utc': None
        }
        location['tz'] = 'America/Los_Angeles'
        self.assertIsInstance(get_mycroft_compatible_location(location), dict)
        location['tz'] = None
        location['city'] = 'Renton'
        self.assertIsInstance(get_mycroft_compatible_location(location), dict)
        location['city'] = None
        location['lat'] = '47.4799078'
        location['lng'] = '-122.2034496'
        self.assertIsInstance(get_mycroft_compatible_location(location), dict)
        shutil.move(old_user_info, ngi_user_info)

    def test_get_user_config_from_mycroft_conf(self):
        from neon_utils.configuration_utils import \
            get_user_config_from_mycroft_conf
        config = get_user_config_from_mycroft_conf()
        self.assertIsInstance(config, dict)
        # TODO: Better tests of config load

    @mock.patch('neon_utils.packaging_utils.get_neon_core_root')
    def test_init_ovos_conf(self, get_core_root):
        default_config = join(dirname(__file__), "configuration", "neon_core")
        get_core_root.return_value = default_config
        test_config_dir = join(dirname(__file__), "test_config")
        from neon_utils.configuration_utils import _init_ovos_conf
        os.environ["XDG_CONFIG_HOME"] = test_config_dir

        if isfile(join(test_config_dir, "OpenVoiceOS", "ovos.conf")):
            os.remove(join(test_config_dir, "OpenVoiceOS", "ovos.conf"))

        # Init 'test_module' to use 'neon_core' config
        _init_ovos_conf("test_module")

        with open(join(test_config_dir, "OpenVoiceOS", "ovos.conf")) as f:
            config = json.load(f)

        # Patch local tests
        config['module_overrides']['neon_core'].setdefault(
            'default_config_path', "")

        self.assertEqual(config, {"module_overrides": {
            "neon_core": {
                "base_folder": "neon",
                "config_filename": "neon.yaml",
                "default_config_path": config['module_overrides']['neon_core'][
                    'default_config_path']
            }
        },
            "submodule_mappings": {
                "test_module": "neon_core"
            }})

        # init same module again, config should be unchanged
        _init_ovos_conf("test_module")
        with open(join(test_config_dir, "OpenVoiceOS", "ovos.conf")) as f:
            config2 = json.load(f)
        # Patch local tests
        config2['module_overrides']['neon_core'].setdefault(
            'default_config_path', "")
        self.assertEqual(config, config2)

        # init another different module
        _init_ovos_conf("other_test_mod")
        with open(join(test_config_dir, "OpenVoiceOS", "ovos.conf")) as f:
            config3 = json.load(f)
            # Patch local tests
            config3['module_overrides']['neon_core'].setdefault(
                'default_config_path', "")
        self.assertEqual(config3, {"module_overrides": {
            "neon_core": {
                "base_folder": "neon",
                "config_filename": "neon.yaml",
                "default_config_path": config['module_overrides']['neon_core'][
                    'default_config_path']
            }
        },
            "submodule_mappings": {
                "test_module": "neon_core",
                "other_test_mod": "neon_core"
            }})

        # init neon_core
        _init_ovos_conf("neon_core")
        with open(join(test_config_dir, "OpenVoiceOS", "ovos.conf")) as f:
            config4 = json.load(f)
            # Patch local tests
            config4['module_overrides']['neon_core'].setdefault(
                'default_config_path', "")
        self.assertEqual(config4, {"module_overrides": {
            "neon_core": {
                "base_folder": "neon",
                "config_filename": "neon.yaml",
                "default_config_path": config['module_overrides']['neon_core'][
                    'default_config_path']
            }
        },
            "submodule_mappings": {
                "test_module": "neon_core",
                "other_test_mod": "neon_core",
                "neon_core": "neon_core",
                "neon_core.skills.skill_manager": "neon_core"
            }})

        # Override default config with test file
        import inspect
        import ovos_config.models
        import ovos_config.config
        from ovos_config.meta import get_ovos_config

        ovos_config.DEFAULT_CONFIG = join(dirname(__file__),
                                          "configuration", "mycroft.conf")
        old_value = deepcopy(ovos_config.DEFAULT_CONFIG)

        # Init config and validate other config file is loaded
        stack = inspect.stack()
        mod = inspect.getmodule(stack[1][0])
        this_modname = mod.__name__.split('.')[0]
        _init_ovos_conf(this_modname)
        self.assertNotEqual(old_value, ovos_config.DEFAULT_CONFIG)
        self.assertEqual(ovos_config.models.DEFAULT_CONFIG,
                         ovos_config.DEFAULT_CONFIG)
        self.assertEqual(ovos_config.config.Configuration.default.path,
                         ovos_config.DEFAULT_CONFIG)

        # Test default config
        self.assertTrue(ovos_config.config.Configuration()['default_config'])
        self.assertEqual(get_ovos_config()['default_config_path'],
                         join(default_config, "configuration", "neon.yaml"))

        # Cleanup configuration and force reload of pre-test defaults
        os.environ.pop("XDG_CONFIG_HOME")
        shutil.rmtree(test_config_dir)
        del ovos_config.config.Configuration
        importlib.reload(ovos_config.locations)
        importlib.reload(ovos_config.models)
        importlib.reload(ovos_config.config)

    def test_validate_config_env(self):
        from neon_utils.configuration_utils import _validate_config_env
        os.environ["XDG_CONFIG_HOME"] = ""

        # Valid default path
        _validate_config_env()
        self.assertEqual(os.environ["NEON_CONFIG_PATH"],
                         expanduser("~/.config/neon"))

        # Invalid neon spec
        os.environ["NEON_CONFIG_PATH"] = "/tmp"
        _validate_config_env()
        self.assertEqual(os.environ["NEON_CONFIG_PATH"],
                         expanduser("~/.config/neon"))

        # Valid neon spec
        os.environ["NEON_CONFIG_PATH"] = "/tmp/neon/neon"
        _validate_config_env()
        self.assertEqual(os.environ["NEON_CONFIG_PATH"], "/tmp/neon/neon")
        self.assertEqual(os.environ["XDG_CONFIG_HOME"], "/tmp/neon")

        # Valid XDG override, Valid Neon spec
        os.environ["XDG_CONFIG_HOME"] = "/tmp/xdg"
        _validate_config_env()
        self.assertEqual(os.environ["NEON_CONFIG_PATH"], "/tmp/xdg/neon")
        self.assertEqual(os.environ["XDG_CONFIG_HOME"], "/tmp/xdg")

        # Valid XDG override, No Neon spec
        os.environ["NEON_CONFIG_PATH"] = ""
        _validate_config_env()
        self.assertEqual(os.environ["NEON_CONFIG_PATH"], "/tmp/xdg/neon")
        self.assertEqual(os.environ["XDG_CONFIG_HOME"], "/tmp/xdg")

        # Valid XDG Override, relocate Neon-spec config
        os.environ["XDG_CONFIG_HOME"] = "/tmp/neon_config"
        os.environ["NEON_CONFIG_PATH"] = join(dirname(__file__),
                                              "test_migrate_config")
        _validate_config_env()
        self.assertEqual(os.environ["NEON_CONFIG_PATH"],
                         "/tmp/neon_config/neon")
        with open(join(dirname(__file__), "test_migrate_config",
                       "ngi_local_conf.yml")) as f:
            actual = f.read()
        with open("/tmp/neon_config/neon/ngi_local_conf.yml") as f:
            migrated = f.read()
        self.assertEqual(actual, migrated)
        shutil.rmtree("/tmp/neon_config")

        os.environ.pop("XDG_CONFIG_HOME")

    def test_migrate_ngi_config(self):
        from neon_utils.configuration_utils import migrate_ngi_config
        test_dir = join(dirname(__file__), "test_migrate_config")
        new_conf = join(test_dir, "neon.yaml")
        os.environ["XDG_CONFIG_PATH"] = test_dir

        # Spec old config dir
        migrate_ngi_config(test_dir, join(test_dir, "neon.yaml"))
        self.assertTrue(isfile(new_conf))
        with open(join(test_dir, "ngi_local_conf.yml")) as f:
            try:
                old_config = yaml.safe_load(f)
            except Exception as e:
                LOG.error(e)
                from ruamel.yaml import YAML
                f.seek(0)
                old_config = json.loads(json.dumps(YAML().load(f)))
        with open(new_conf) as f:
            new_config = yaml.safe_load(f)
        last_change = getmtime(new_conf)
        self.assertEqual(new_config.get('device_name'),
                         old_config["devVars"]['devName'])
        self.assertEqual(new_config['hotwords'], old_config['hotwords'])
        for setting in old_config['listener']:
            self.assertEqual(old_config['listener'][setting],
                             new_config['listener'][setting])
        self.assertEqual(old_config['logs']['log_level'],
                         new_config['log_level'])
        for setting in old_config['stt']:
            self.assertEqual(old_config['stt'][setting],
                             new_config['stt'][setting])
        for setting in old_config['tts']:
            self.assertEqual(old_config['tts'][setting],
                             new_config['tts'][setting])
        self.assertEqual(old_config["MQ"], new_config["MQ"])

        # Spec old config file
        migrate_ngi_config(join(test_dir, "ngi_local_conf.yml"), new_conf)
        with open(new_conf) as f:
            newer_config = yaml.safe_load(f)
        self.assertNotEqual(last_change, getmtime(new_conf))
        self.assertEqual(new_config, newer_config)

        os.remove(new_conf)

    @mock.patch('neon_utils.packaging_utils.get_neon_core_root')
    def test_get_neon_yaml_config(self, get_core_root):
        config_dir = join(dirname(__file__), "configuration",
                          "get_neon_yaml_config")
        get_core_root.return_value = join(config_dir, "default")
        os.environ["XDG_CONFIG_HOME"] = config_dir
        os.environ["MYCROFT_SYSTEM_CONFIG"] = join(config_dir, "system",
                                                   "neon.yaml")
        from neon_utils.configuration_utils import _get_neon_yaml_config, \
            init_config_dir
        init_config_dir()
        config = _get_neon_yaml_config()
        self.assertEqual(config,
                         {"config": "user",
                          "from_default": True,
                          "from_system": True,
                          "user": {
                              "from_system": True,
                              "from_default": True,
                              "from_user": True,
                              "not_from_user": False
                          }})
        shutil.rmtree(join(config_dir, "OpenVoiceOS"))


class DeprecatedConfigTests(unittest.TestCase):
    def doCleanups(self) -> None:
        if os.getenv("NEON_CONFIG_PATH"):
            os.environ.pop("NEON_CONFIG_PATH")
        for file in glob(os.path.join(CONFIG_PATH, ".*.lock")):
            os.remove(file)
        for file in glob(os.path.join(CONFIG_PATH, ".*.tmp")):
            os.remove(file)
        for file in glob(os.path.join(ROOT_DIR, "credentials", ".*.lock")):
            os.remove(file)
        for file in glob(os.path.join(ROOT_DIR, "credentials", ".*.tmp")):
            os.remove(file)
        if os.path.exists(os.path.join(CONFIG_PATH, "old_user_info.yml")):
            os.remove(os.path.join(CONFIG_PATH, "old_user_info.yml"))

    def test_get_audio_config(self):
        from neon_utils.configuration_utils import _get_neon_audio_config
        config = _get_neon_audio_config()
        self.assertIsInstance(config, dict)
        self.assertIsInstance(config["Audio"], dict)
        self.assertIsInstance(config["tts"], dict)
        self.assertIsInstance(config["language"], dict)

    def test_get_gui_config(self):
        from neon_utils.configuration_utils import _get_neon_gui_config
        config = _get_neon_gui_config()
        self.assertIsInstance(config, dict)
        # self.assertIsInstance(config["lang"], str)
        # self.assertIsInstance(config["enclosure"], str)
        # self.assertIsInstance(config["host"], str)
        # self.assertIsInstance(config["port"], int)
        # self.assertIsInstance(config["base_port"], int)
        # self.assertIsInstance(config["route"], str)
        # self.assertIsInstance(config["ssl"], bool)
        # self.assertIsInstance(config["resource_root"], str)
        # self.assertIn("file_server", config.keys())
        # self.assertEqual(config["port"], config["base_port"])

    def test_get_lang_config(self):
        from neon_utils.configuration_utils import _get_neon_lang_config
        config = _get_neon_lang_config()
        self.assertIsInstance(config, dict)
        # self.assertIn("internal", config)
        # self.assertIn("user", config)
        # self.assertIn("detection_module", config)
        # self.assertIn("translation_module", config)
        # self.assertIn("boost", config)
        # self.assertIsInstance(config["libretranslate"], dict)

    def test_get_transcribe_config(self):
        from neon_utils.configuration_utils import _get_neon_transcribe_config
        config = _get_neon_transcribe_config()
        self.assertIsInstance(config, dict)
        self.assertIsInstance(config["audio_permission"], bool)
        self.assertIsInstance(config["transcript_dir"], str)

    def test_get_tts_config(self):
        from neon_utils.configuration_utils import _get_neon_tts_config
        config = _get_neon_tts_config()
        self.assertIsInstance(config, dict)
        # self.assertIsInstance(config["module"], str)
        # self.assertIsInstance(config[config["module"]], dict)

    def test_get_skills_config(self):
        from neon_utils.configuration_utils import _get_neon_skills_config
        config = _get_neon_skills_config()
        self.assertIsInstance(config["debug"], bool)
        self.assertIsInstance(config["blacklisted_skills"], list)
        self.assertIsInstance(config["priority_skills"], list)
        self.assertIsInstance(config["update_interval"], float)
        # self.assertIsInstance(config["data_dir"], str)
        # self.assertIsInstance(config["skill_manager"], str)

        # self.assertIsInstance(config["install_default"], bool)
        # self.assertIsInstance(config["install_essential"], bool)
        # self.assertIn("default_skills", config)
        # self.assertIn("essential_skills", config)
        # self.assertIn("neon_token", config)

        self.assertEqual(config["update_interval"],
                         config["auto_update_interval"])  # Backwards Compat.
        # self.assertIsInstance(config["directory"], str)
        # self.assertIsInstance(config["extra_directories"], list)
        # self.assertIsInstance(config["disable_osm"], bool)

        if config.get("msm"):
            self.assertIsInstance(config["msm"], dict)
            # self.assertIsInstance(config["msm"]["directory"], str)
            self.assertIsInstance(config["msm"]["versioned"], bool)
            self.assertIsInstance(config["msm"]["repo"], dict)

            self.assertIsInstance(config["msm"]["repo"]["branch"], str)
            self.assertIsInstance(config["msm"]["repo"]["cache"], str)
            self.assertIsInstance(config["msm"]["repo"]["url"], str)

    def test_added_module_config(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        bak_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.bak")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")
        ngi_test_conf = os.path.join(CONFIG_PATH,
                                     "local_conf_with_stt_tts.yml")

        shutil.move(ngi_local_conf, bak_local_conf)
        shutil.copy(ngi_test_conf, ngi_local_conf)
        local_config = _get_neon_local_config(CONFIG_PATH)
        self.assertEqual(local_config["tts"]["mozilla_remote"],
                         {"url": "http://something.somewhere"})
        self.assertEqual(local_config["stt"]["some_module"], {"key": "value"})
        # self.assertIn("dirVars", local_config.content.keys())
        shutil.move(bak_local_conf, ngi_local_conf)

    def test_move_language_config(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        bak_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.bak")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")
        ngi_test_conf = os.path.join(CONFIG_PATH, "local_conf_no_language.yml")

        shutil.move(ngi_local_conf, bak_local_conf)
        shutil.copy(ngi_test_conf, ngi_local_conf)
        local_config = _get_neon_local_config(CONFIG_PATH)
        self.assertEqual(local_config["language"]["translation_module"],
                         "old_translate_module")
        self.assertEqual(local_config["language"]["detection_module"],
                         "old_detection_module")
        # self.assertIsInstance(local_config["language"]["libretranslate"], dict)
        self.assertIn("dirVars", local_config.content.keys())
        shutil.move(bak_local_conf, ngi_local_conf)

    def test_added_hotwords_config(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        bak_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.bak")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")

        test_hotword_config = {"listen": True,
                               "model": "model_path"}

        shutil.move(ngi_local_conf, bak_local_conf)
        local_config = _get_neon_local_config(CONFIG_PATH)
        local_config.content.setdefault('hotwords', {})
        hotwords_config = deepcopy(local_config["hotwords"])
        local_config['hotwords']["test_hotword"] = test_hotword_config
        for hotword, config in hotwords_config.items():
            self.assertEqual(local_config['hotwords'][hotword], config)

        fresh_config = _get_neon_local_config(CONFIG_PATH)
        self.assertEqual(fresh_config.content, local_config.content)
        self.assertEqual(fresh_config['hotwords']['test_hotword'],
                         test_hotword_config)

        shutil.move(bak_local_conf, ngi_local_conf)

    def test_get_neon_auth_config(self):
        from neon_utils.authentication_utils import find_neon_aws_keys,\
            find_neon_google_keys, find_neon_git_token, find_neon_wolfram_key,\
            find_neon_alpha_vantage_key, find_neon_owm_key
        from neon_utils.configuration_utils import _get_neon_auth_config
        auth_path = os.path.join(ROOT_DIR, "credentials")
        ngi_auth_vars = _get_neon_auth_config(auth_path)
        self.assertEqual(ngi_auth_vars["amazon"],
                         find_neon_aws_keys(auth_path))
        self.assertEqual(ngi_auth_vars["google"],
                         find_neon_google_keys(auth_path))
        self.assertEqual(ngi_auth_vars["github"],
                         {"token": find_neon_git_token(auth_path)})
        self.assertEqual(ngi_auth_vars["wolfram"],
                         {"app_id": find_neon_wolfram_key(auth_path)})
        self.assertEqual(ngi_auth_vars["alpha_vantage"],
                         {"api_key": find_neon_alpha_vantage_key(auth_path)})
        self.assertEqual(ngi_auth_vars["owm"],
                         {"api_key": find_neon_owm_key(auth_path)})

    def test_get_neon_auth_config_unwritable(self):
        from neon_utils.configuration_utils import _get_neon_auth_config, \
            get_config_dir
        real_auth_config = join(get_config_dir(), "ngi_auth_vars.yml")
        bak_auth_config = join(get_config_dir(), "ngi_auth.bak")
        if isfile(real_auth_config):
            shutil.copy(real_auth_config, bak_auth_config)
        os.environ["NEON_CONFIG_PATH"] = os.path.join(ROOT_DIR,
                                                      "configuration",
                                                      "unwritable_path")
        ngi_auth_vars = _get_neon_auth_config()
        self.assertIsInstance(ngi_auth_vars, dict)

        if isfile(bak_auth_config):
            shutil.move(bak_auth_config, real_auth_config)

    def test_safe_mycroft_config(self):
        from neon_utils.configuration_utils import _safe_mycroft_config

        config = _safe_mycroft_config()
        self.assertIsInstance(config, dict)
        self.assertIn("skills", config)

    def test_populate_read_only_config_no_overwrite(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        from neon_utils.configuration_utils import _populate_read_only_config
        test_dir = os.path.join(ROOT_DIR, "configuration", "populate_tests")
        ro_dir = os.path.join(test_dir, "test_ro_dir")
        test_conf = _get_neon_local_config(test_dir)
        test_filename = basename(test_conf.file_path)

        self.assertFalse(_populate_read_only_config(test_dir,
                                                    test_filename, test_conf))

        os.chdir(test_dir)
        self.assertFalse(_populate_read_only_config("./",
                                                    test_filename, test_conf))
        self.assertFalse(_populate_read_only_config(None,
                                                    test_filename, test_conf))
        self.assertFalse(_populate_read_only_config(ro_dir,
                                                    test_filename, test_conf))
        os.remove(test_conf.file_path)

    def test_default_config(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        config = _get_neon_local_config("/tmp/neon/test/")
        self.assertIsInstance(config.content, dict)
        # import requests
        # resp = requests.get(config["skills"]["default_skills"])
        # self.assertTrue(resp.ok)

    def test_simultaneous_config_updates(self):
        from neon_utils.configuration_utils import _get_neon_lang_config, \
            _get_neon_local_config, get_neon_user_config
        from threading import Thread
        test_results = {}

        config_path = join(CONFIG_PATH, "depreciated_language_config")
        backup_path = join(CONFIG_PATH, "backup_config")
        os.environ["NEON_CONFIG_PATH"] = config_path
        if isdir(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(config_path, backup_path)

        def _open_config(idx):
            success = True
            try:
                local_config = \
                    deepcopy(_get_neon_local_config(config_path).content)
                self.assertNotIn("translation_module", local_config["stt"])
                self.assertNotIn("detection_module", local_config["stt"])
            except Exception as e:
                LOG.error(e)
                success = False
            try:
                user_config = get_neon_user_config(config_path)
                self.assertNotIn("listener", user_config.content.keys())
            except Exception as e:
                LOG.error(e)
                success = False
            try:
                lang_config = _get_neon_lang_config()
                self.assertIsInstance(lang_config["boost"], bool)
            except Exception as e:
                LOG.error(e)
                success = False
            test_results[idx] = success

        for i in range(64):
            Thread(target=_open_config, args=(i,), daemon=True).start()
        while not len(test_results.keys()) == 64:
            sleep(0.5)
        self.assertTrue(all(test_results.values()))

        shutil.rmtree(config_path)
        shutil.move(backup_path, config_path)

    def test_unequal_cache_configs(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        bak_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.bak")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")
        shutil.copy(ngi_local_conf, bak_local_conf)

        def_config = _get_neon_local_config(f"{ROOT_DIR}/test")
        oth_config = _get_neon_local_config(CONFIG_PATH)
        self.assertNotEqual(def_config, oth_config)
        self.assertNotEqual(def_config.content, oth_config.content)

        if isdir(f"{ROOT_DIR}/test"):
            shutil.rmtree(f"{ROOT_DIR}/test")
        shutil.move(bak_local_conf, ngi_local_conf)


    def test_get_local_config_add_keys(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        old_local_conf = os.path.join(CONFIG_PATH, "old_local_conf.yml")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")
        shutil.copy(ngi_local_conf, old_local_conf)
        config = _get_neon_local_config(CONFIG_PATH)
        local_config_keys = ["prefFlags", "interface", "devVars", "gestures",
                             "audioService", "padatious", "websocket",
                             "gui", "hotwords", "listener", "skills",
                             "session", "tts", "stt", "logs", "device"]
        self.assertTrue(all(k for k in local_config_keys if k in config))
        shutil.move(old_local_conf, ngi_local_conf)

    def test_get_local_config_create(self):
        from neon_utils.configuration_utils import _get_neon_local_config
        old_local_conf = os.path.join(CONFIG_PATH, "old_local_conf.yml")
        ngi_local_conf = os.path.join(CONFIG_PATH, "ngi_local_conf.yml")
        shutil.move(ngi_local_conf, old_local_conf)
        config = _get_neon_local_config(CONFIG_PATH)
        local_config_keys = ["prefFlags", "interface", "devVars", "gestures",
                             "audioService", "padatious", "websocket",
                             "gui", "hotwords", "listener", "skills",
                             "session", "tts", "stt", "logs", "device"]
        self.assertTrue(all(k for k in local_config_keys if k in config))
        shutil.move(old_local_conf, ngi_local_conf)


if __name__ == '__main__':
    unittest.main()
