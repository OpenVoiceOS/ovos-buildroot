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

from threading import Event
from os.path import join, dirname

import ovos_utils.signal
from mycroft_bus_client import Message
from ovos_utils.messagebus import FakeBus

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import neon_utils.signal_utils


class TestSignalManager:
    def __init__(self, bus):
        self.bus = bus
        self._register_listeners()
        self.bus.run_in_thread()

    def _register_listeners(self):
        """
        Register Event Handlers
        """
        self.bus.on("neon.create_signal", self._handle_create_signal)
        self.bus.on("neon.check_for_signal", self._handle_check_for_signal)
        self.bus.on("neon.wait_for_signal_create", self._handle_wait_for_signal_create)
        self.bus.on("neon.wait_for_signal_clear", self._handle_wait_for_signal_clear)
        self.bus.on("neon.signal_manager_active", self._handle_signal_manager_active)

    def _handle_create_signal(self, message: Message):
        signal_name = message.data["signal_name"]
        status = True
        self.bus.emit(message.reply(f"neon.create_signal.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_check_for_signal(self, message: Message):
        signal_name = message.data["signal_name"]
        status = True
        self.bus.emit(message.reply(f"neon.check_for_signal.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_wait_for_signal_create(self, message: Message):
        signal_name = message.data["signal_name"]
        status = True
        self.bus.emit(message.reply(f"neon.wait_for_signal_create.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_wait_for_signal_clear(self, message: Message):
        signal_name = message.data["signal_name"]
        status = False
        self.bus.emit(message.reply(f"neon.wait_for_signal_clear.{signal_name}",
                                    data={"signal_name": signal_name,
                                          "is_set": status}))

    def _handle_signal_manager_active(self, message: Message):
        self.bus.emit(message.response())


class SignalUtilsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        test_ipc_dir = join(dirname(__file__), "signal_tests")
        cls.test_config = {"ipc_path": test_ipc_dir}
        # cls.manager = None

    def setUp(self):
        self.test_bus = FakeBus()
        self.test_bus.connected_event = Event()
        self.test_bus.connected_event.set()
        self.test_bus.run_in_thread()
        neon_utils.signal_utils.init_signal_bus(self.test_bus)
        neon_utils.signal_utils.init_signal_handlers()

    def test_signal_file(self):
        self.assertTrue(neon_utils.signal_utils.create_signal("test", self.test_config))
        self.assertTrue(neon_utils.signal_utils.check_for_signal("test", -1, self.test_config))
        self.assertTrue(neon_utils.signal_utils.check_for_signal("test", 0, self.test_config))
        self.assertFalse(neon_utils.signal_utils.check_for_signal("test", -1, self.test_config))

    def test_check_signal_manager_available(self):
        self.assertFalse(neon_utils.signal_utils.check_signal_manager_available())

        TestSignalManager(self.test_bus)
        self.assertTrue(neon_utils.signal_utils.check_signal_manager_available())

    def test_signal_manager_message_context(self):
        msg = None

        def on_create(message):
            nonlocal msg
            msg = message

        TestSignalManager(self.test_bus)
        neon_utils.signal_utils.init_signal_handlers()
        self.test_bus.once("neon.create_signal", on_create)
        from neon_utils.signal_utils import create_signal
        create_signal("test_signal")
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data, {'signal_name': 'test_signal'})
        self.assertEqual(msg.context,
                         {'origin_module': 'tests.signal_util_tests',
                          'origin_line': 130})

    def test_signal_utils_manager_available(self):
        TestSignalManager(self.test_bus)
        neon_utils.signal_utils.init_signal_handlers()
        self.assertEqual(neon_utils.signal_utils._BUS, self.test_bus)
        self.assertIsInstance(neon_utils.signal_utils._MAX_TIMEOUT, int)
        self.assertTrue(neon_utils.signal_utils.check_signal_manager_available())

        # Check neon_utils references
        self.assertEqual(neon_utils.signal_utils._check_for_signal,
                         neon_utils.signal_utils._manager_check_for_signal)
        self.assertEqual(neon_utils.signal_utils._create_signal,
                         neon_utils.signal_utils._manager_create_signal)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_clear,
                         neon_utils.signal_utils._manager_wait_for_signal_clear)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_create,
                         neon_utils.signal_utils._manager_wait_for_signal_create)

        # Check ovos_utils references
        self.assertEqual(ovos_utils.signal.check_for_signal,
                         neon_utils.signal_utils._manager_check_for_signal)
        self.assertEqual(ovos_utils.signal.create_signal,
                         neon_utils.signal_utils._manager_create_signal)

    def test_signal_utils_manager_unavailable(self):
        import ovos_utils.signal
        neon_utils.signal_utils.init_signal_handlers()
        self.assertFalse(neon_utils.signal_utils.check_signal_manager_available())
        self.assertIsInstance(neon_utils.signal_utils._MAX_TIMEOUT, int)
        self.assertEqual(neon_utils.signal_utils._check_for_signal,
                         ovos_utils.signal.check_for_signal)
        self.assertEqual(neon_utils.signal_utils._create_signal,
                         ovos_utils.signal.create_signal)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_clear,
                         neon_utils.signal_utils._fs_wait_for_signal_clear)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_create,
                         neon_utils.signal_utils._fs_wait_for_signal_create)

    def test_signal_utils_reload(self):
        import ovos_utils.signal
        from neon_utils.signal_utils import _check_for_signal
        self.assertFalse(neon_utils.signal_utils.check_signal_manager_available())
        self.assertEqual(neon_utils.signal_utils._check_for_signal,
                         ovos_utils.signal.check_for_signal)
        self.assertEqual(neon_utils.signal_utils._create_signal,
                         ovos_utils.signal.create_signal)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_clear,
                         neon_utils.signal_utils._fs_wait_for_signal_clear)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_create,
                         neon_utils.signal_utils._fs_wait_for_signal_create)
        self.assertEqual(_check_for_signal,
                         ovos_utils.signal.check_for_signal)

        TestSignalManager(self.test_bus)
        neon_utils.signal_utils.init_signal_handlers()
        self.assertEqual(neon_utils.signal_utils._check_for_signal,
                         neon_utils.signal_utils._manager_check_for_signal)
        self.assertEqual(neon_utils.signal_utils._create_signal,
                         neon_utils.signal_utils._manager_create_signal)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_clear,
                         neon_utils.signal_utils._manager_wait_for_signal_clear)
        self.assertEqual(neon_utils.signal_utils._wait_for_signal_create,
                         neon_utils.signal_utils._manager_wait_for_signal_create)

        # Previously imported method is not updated
        self.assertEqual(_check_for_signal,
                         ovos_utils.signal.check_for_signal)

    def test_check_signal_manager_available_lazy_load_bus(self):
        from mycroft_bus_client import MessageBusClient
        from neon_utils.signal_utils import check_signal_manager_available
        neon_utils.signal_utils._BUS = None
        neon_utils.signal_utils.check_signal_manager_available()
        self.assertIsInstance(neon_utils.signal_utils._BUS, MessageBusClient)
        self.assertIsInstance(neon_utils.signal_utils._MAX_TIMEOUT, int)


if __name__ == '__main__':
    unittest.main()
