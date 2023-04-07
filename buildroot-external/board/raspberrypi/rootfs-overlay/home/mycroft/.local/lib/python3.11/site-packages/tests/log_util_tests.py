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

import io
import logging
import os
import sys
import shutil
import unittest

from os.path import basename, isdir
from time import time, sleep
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG_PATH = os.path.join(ROOT_DIR, "tests", "log_files")


class LogUtilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ['XDG_CONFIG_HOME'] = '/tmp'
        os.makedirs(LOG_PATH, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop('XDG_CONFIG_HOME')
        shutil.rmtree(LOG_PATH)

    def test_get_log_file(self):
        from neon_utils.log_utils import get_logger
        log = get_logger("test", LOG_PATH)
        log.level = logging.DEBUG
        test_msg = "This should be in test.log"
        log.debug(test_msg)
        with open(os.path.join(LOG_PATH, "test.log")) as log:
            contents = log.read()
        self.assertTrue(contents.endswith(f"{test_msg}\n"))

    def test_get_log_file_with_stdout(self):
        from neon_utils.log_utils import get_logger
        normal_stdout = sys.stdout
        captured_out = io.StringIO()
        sys.stdout = captured_out
        log = get_logger("test_stdout", LOG_PATH, True)
        log.level = logging.DEBUG
        test_msg = "This should be in test.log and stdout"
        log.debug(test_msg)
        with open(os.path.join(LOG_PATH, "test_stdout.log")) as log:
            contents = log.read()
        logged = captured_out.getvalue().strip("\n")
        sys.stdout = normal_stdout
        self.assertTrue(contents.endswith(f"{test_msg}\n"))
        self.assertEqual(logged, contents.split("\n")[-2])

    def test_get_log_no_file(self):
        from neon_utils.log_utils import get_logger
        logs = os.listdir(LOG_PATH)
        normal_stdout = sys.stdout
        captured_out = io.StringIO()
        sys.stdout = captured_out
        log = get_logger("terminal_only", "stdout")
        log.level = logging.DEBUG
        test_msg = "This should be in stdout ONLY"
        log.debug(test_msg)
        logged = captured_out.getvalue().strip("\n")
        sys.stdout = normal_stdout
        self.assertTrue(logged.endswith(test_msg))
        self.assertEqual(logs, os.listdir(LOG_PATH))

    def test_archive_logs_default(self):
        from neon_utils.log_utils import archive_logs
        os.makedirs(LOG_PATH, exist_ok=True)
        test_log = os.path.join(LOG_PATH, "to_backup.log")
        with open(test_log, "w+") as f:
            f.write("TEST LOG")
        archive_logs(LOG_PATH)
        for path in os.listdir(LOG_PATH):
            if os.path.isdir(os.path.join(LOG_PATH, path)):
                self.assertTrue(os.path.isfile(os.path.join(LOG_PATH, path, "to_backup.log")))
                return
        self.assertTrue(False)

    def test_archive_logs_specific(self):
        from neon_utils.log_utils import archive_logs
        os.makedirs(LOG_PATH, exist_ok=True)
        test_log = os.path.join(LOG_PATH, "to_backup.log")
        with open(test_log, "w+") as f:
            f.write("TEST LOG")
        archive_logs(LOG_PATH, "backup")
        path = os.path.join(LOG_PATH, "backup")
        self.assertTrue(os.path.isfile(os.path.join(LOG_PATH, path, "to_backup.log")))

    def test_remove_old_logs(self):
        from neon_utils.log_utils import archive_logs, remove_old_logs, init_log_for_module
        init_log_for_module(std_out=True)
        os.makedirs(LOG_PATH, exist_ok=True)
        test_log = os.path.join(LOG_PATH, "to_be_removed.log")
        with open(test_log, "w+") as f:
            f.write("TEST LOG")
        archive_logs(LOG_PATH)
        old_log_time = time()
        sleep(1)

        test_log = os.path.join(LOG_PATH, "to_be_retained.log")
        with open(test_log, "w+") as f:
            f.write("TEST LOG")
        archive_logs(LOG_PATH)

        remove_old_logs(LOG_PATH, timedelta(seconds=time() - old_log_time))
        self.assertEqual(len([p for p in os.listdir(LOG_PATH) if os.path.isdir(os.path.join(LOG_PATH, p))]), 1)
        for path in os.listdir(LOG_PATH):
            if os.path.isdir(os.path.join(LOG_PATH, path)):
                self.assertTrue(os.path.isfile(os.path.join(LOG_PATH, path, "to_be_retained.log")))
                return

    def test_get_log_file_for_module(self):
        from neon_utils.log_utils import get_log_file_for_module
        self.assertEqual("voice.log", os.path.basename(get_log_file_for_module("neon_speech_client")))
        self.assertEqual("voice.log", os.path.basename(get_log_file_for_module("neon_speech")))
        self.assertEqual("bus.log", os.path.basename(get_log_file_for_module(["python3", "-m",
                                                                              "mycroft.messagebus.service"])))
        self.assertEqual("bus.log", os.path.basename(get_log_file_for_module("neon_messagebus_service")))
        self.assertEqual("skills.log", os.path.basename(get_log_file_for_module("mycroft.skills")))
        self.assertEqual("skills.log", os.path.basename(get_log_file_for_module("neon_skills_service")))
        self.assertEqual("gui.log", os.path.basename(get_log_file_for_module("mycroft-gui-app")))
        self.assertEqual("display.log", os.path.basename(get_log_file_for_module("neon_gui_service")))
        self.assertEqual("display.log", os.path.basename(get_log_file_for_module("neon_core.gui")))

        self.assertEqual("extras.log", os.path.basename(get_log_file_for_module("NGI.gui")))
        self.assertEqual("extras.log", os.path.basename(get_log_file_for_module("nothing")))

    def test_init_log_for_module(self):
        from neon_utils.log_utils import init_log_for_module, ServiceLog, LOG
        init_log_for_module(ServiceLog.SPEECH)
        self.assertEqual(basename(LOG.base_path), ServiceLog.SPEECH.value)
        init_log_for_module(ServiceLog.AUDIO, True)
        self.assertEqual(LOG.base_path, "stdout")
        init_log_for_module(ServiceLog.AUDIO)
        self.assertEqual(basename(LOG.base_path), ServiceLog.AUDIO.value)

        from neon_utils.logger import LOG as neon_log
        from ovos_utils.log import LOG as ovos_log
        self.assertEqual(neon_log, ovos_log)
        self.assertEqual(neon_log, LOG)

    def test_get_log_dir(self):
        from neon_utils.log_utils import get_log_dir
        log_dir = get_log_dir()
        self.assertTrue(isdir(log_dir))

    def test_init_log(self):
        from neon_utils.log_utils import init_log
        config = {'log_level': 'DEBUG',
                  "logs": {
                      "name": "neon-utils"
                  }}
        log = init_log(config)
        self.assertEqual(log.name, "neon-utils")
        self.assertEqual(log.level, "DEBUG")
        from ovos_utils.log import LOG as OLOG
        from neon_utils.logger import LOG as NLOG
        self.assertEqual(OLOG, log)
        self.assertEqual(NLOG, log)

        config['log_level'] = 'INFO'
        config['logs']['name'] = 'test'
        config['logs']['level_overrides'] = {
            'error': ['filelock']
        }
        new_log = init_log(config)
        self.assertEqual(log, new_log)
        self.assertEqual(log.name, "test")
        self.assertEqual(log.level, "INFO")
        self.assertEqual(logging.getLogger('filelock').level, logging.ERROR)
        self.assertEqual(OLOG, log)
        self.assertEqual(NLOG, log)

    def test_get_log(self):
        from neon_utils.log_utils import get_log
        from ovos_utils.log import LOG as OLOG
        from neon_utils.log_utils import LOG as NLOG
        self.assertEqual(get_log(), OLOG)
        self.assertEqual(get_log(), NLOG)


if __name__ == '__main__':
    unittest.main()
