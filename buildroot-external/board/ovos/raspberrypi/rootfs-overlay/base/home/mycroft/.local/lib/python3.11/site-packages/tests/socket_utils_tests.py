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
import socket
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.logger import LOG
from neon_utils.socket_utils import *

TEST_DICT = {b"section 1": {"key1": "val1",
                            "key2": "val2"},
             "section 2": {"key_1": b"val1",
                           "key_2": f"val2"}}

TEST_DICT_B64 = b'IntiJ3NlY3Rpb24gMSc6IHsna2V5MSc6ICd2YWwxJywgJ2tleTInOiAndmFsMid9LCAnc2VjdGlvbiAyJzogeydrZXlfMSc6IGIndmFsMScsICdrZXlfMic6ICd2YWwyJ319Ig=='

TEST_SOCKET_ADDRESS = ('127.0.0.1', 8999)


class SocketUtilsTest(unittest.TestCase):

    def tcp_client(self):
        """Simple tcp socket client emitting just one message"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(TEST_SOCKET_ADDRESS)
            s.sendall(TEST_DICT_B64)
            LOG.info('Client sent data')
            data = get_packet_data(socket=s, sequentially=True)
            self.assertEqual(data, TEST_DICT_B64)

    def test_01_dict_to_b64(self):
        b64_str = dict_to_b64(TEST_DICT)
        self.assertIsInstance(b64_str, bytes)
        self.assertTrue(len(b64_str) > 0)
        self.assertEqual(b64_str, TEST_DICT_B64)

    def test_02_b64_to_dict(self):
        result_dict = b64_to_dict(TEST_DICT_B64)
        self.assertIsInstance(result_dict, dict)
        self.assertTrue(len(list(result_dict)) > 0)
        self.assertEqual(result_dict, TEST_DICT)

    def test_03_get_packet_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(TEST_SOCKET_ADDRESS)
            s.listen()
            threading.Thread(target=self.tcp_client).start()
            conn, addr = s.accept()
            with conn:
                LOG.info(f'Connected by {addr}')
                data = get_packet_data(conn, sequentially=False)
                self.assertEqual(data, TEST_DICT_B64)
                conn.sendall(data)
