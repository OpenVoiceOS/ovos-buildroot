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
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.authentication_utils import *
from neon_utils.configuration_utils import NGIConfig

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CRED_PATH = os.path.join(ROOT_DIR, "credentials")


class AuthUtilTests(unittest.TestCase):
    def setUp(self) -> None:
        config_path = os.path.join(ROOT_DIR, "configuration")
        self.old_local_conf = os.path.join(config_path, "old_local_conf.yml")
        self.ngi_local_conf = os.path.join(config_path, "ngi_local_conf.yml")
        shutil.copy(self.ngi_local_conf, self.old_local_conf)
        NGIConfig(os.path.splitext(os.path.basename(self.ngi_local_conf))[0],
                  os.path.dirname(self.ngi_local_conf),
                  force_reload=True)

    def tearDown(self) -> None:
        shutil.move(self.old_local_conf, self.ngi_local_conf)

    def test_get_git_token(self):
        try:
            token = find_neon_git_token("/tmp")
            self.assertIsInstance(token, str)
        except Exception as e:
            self.assertIsInstance(e, CredentialNotFoundError)

        token = find_neon_git_token(CRED_PATH)
        self.assertEqual(token, "github token goes here")

        os.environ["GITHUB_TOKEN"] = "test_gh_token"
        self.assertEqual(find_neon_git_token(), "test_gh_token")

    def test_get_aws_credentials(self):
        try:
            keys = find_neon_aws_keys("/tmp")
            self.assertEqual(list(keys.keys()), ["aws_access_key_id",
                                                 "aws_secret_access_key"])
        except Exception as e:
            self.assertIsInstance(e, CredentialNotFoundError)

        keys = find_neon_aws_keys(CRED_PATH)
        self.assertEqual(keys, {"aws_access_key_id": "FAKE_KEY_ID",
                                "aws_secret_access_key": "FAKE_SECRET/"})

        os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_id"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret"
        self.assertEqual(find_neon_aws_keys(),
                         {"aws_access_key_id": "test_aws_id",
                          "aws_secret_access_key": "test_aws_secret"})

    def test_get_google_credentials(self):
        try:
            creds = find_neon_google_keys("/tmp")
            self.assertIsInstance(creds, dict)
        except Exception as e:
            self.assertIsInstance(e, CredentialNotFoundError)

        creds = find_neon_google_keys(CRED_PATH)
        self.assertEqual(list(creds.keys()),
                         ["type", "project_id", "private_key_id",
                          "private_key", "client_email", "client_id",
                          "auth_uri", "token_uri",
                          "auth_provider_x509_cert_url",
                          "client_x509_cert_url"])
        self.assertEqual(creds["private_key"],
                         "-----BEGIN PRIVATE KEY-----\nREDACTED\nREDACTED\n"
                         "REDACTED\n-----END PRIVATE KEY-----\n")

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
            os.path.join(CRED_PATH, "google.json")
        self.assertEqual(find_neon_google_keys(), creds)

    def test_get_wolfram_key(self):
        try:
            key = find_neon_wolfram_key("/tmp")
            self.assertIsInstance(key, str)
        except Exception as e:
            self.assertIsInstance(e, FileNotFoundError)

        key = find_neon_wolfram_key(CRED_PATH)
        self.assertEqual(key, "RED-ACTED")

        os.environ["WOLFRAM_APP_ID"] = "test_wa_id"
        self.assertEqual(find_neon_wolfram_key(), "test_wa_id")

    def test_get_alpha_vantage_key(self):
        try:
            key = find_neon_alpha_vantage_key("/tmp")
            self.assertIsInstance(key, str)
        except Exception as e:
            self.assertIsInstance(e, FileNotFoundError)

        key = find_neon_alpha_vantage_key(CRED_PATH)
        self.assertEqual(key, "Alpha-Vantage")

        os.environ["ALPHA_VANTAGE_KEY"] = "test_av_key"
        self.assertEqual(find_neon_alpha_vantage_key(), "test_av_key")

    def test_get_owm_key(self):
        try:
            key = find_neon_owm_key("/tmp")
            self.assertIsInstance(key, str)
        except Exception as e:
            self.assertIsInstance(e, FileNotFoundError)

        key = find_neon_owm_key(CRED_PATH)
        self.assertEqual(key, "OpenWeatherMap")

        os.environ["OWM_KEY"] = "test_owm_key"
        self.assertEqual(find_neon_owm_key(), "test_owm_key")

    def test_repo_is_neon_valid(self):
        self.assertTrue(repo_is_neon(
            "http://github.com/NeonGeckoCom/alerts.neon"))
        self.assertTrue(repo_is_neon(
            "https://github.com/NeonGeckoCom/caffeinewiz.neon"))
        self.assertTrue(repo_is_neon(
            "ssh://github.com/NeonGeckoCom/launcher.neon"))

        self.assertTrue(repo_is_neon(
            "https://github.com/neondaniel/speedtest.neon"))

        self.assertFalse(repo_is_neon(
            "https://github.com/mycroftai/skill-alarm"))
        self.assertFalse(repo_is_neon(
            "http://gitlab.com/neongecko/some-skill"))

    def test_repo_is_neon_invalid(self):
        with self.assertRaises(ValueError):
            repo_is_neon("https://github.com")
        with self.assertRaises(ValueError):
            repo_is_neon("not a url")
        with self.assertRaises(ValueError):
            repo_is_neon("")

    def test_build_new_auth_config(self):
        config = build_new_auth_config(CRED_PATH)
        self.assertEqual(set(config.keys()), {"github", "amazon", "wolfram",
                                              "google", "alpha_vantage",
                                              "owm"})
        for key in config.keys():
            self.assertIsInstance(config[key], dict)
            self.assertTrue(config[key])

        config = build_new_auth_config("/empty_dir")
        self.assertIsInstance(config, dict)
        for key in config.keys():
            if config[key] is not None:
                self.assertIsInstance(config[key], dict)
                for k, v in config[key].items():
                    self.assertIsInstance(k, str)
                    self.assertIsInstance(v, str)


if __name__ == '__main__':
    unittest.main()
