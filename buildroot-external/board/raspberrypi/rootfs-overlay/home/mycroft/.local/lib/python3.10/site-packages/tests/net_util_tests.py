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

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class NetUtilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from socket import socket
        cls.base_socket = socket

    @classmethod
    def tearDownClass(cls) -> None:
        socket.socket = cls.base_socket

    def setUp(self):
        socket.socket = self.base_socket

    def test_get_ip_address_valid(self):
        from neon_utils.net_utils import get_ip_address

        ip_addr = get_ip_address()
        self.assertIsInstance(ip_addr, str)

    def test_get_ip_address_offline(self):
        def mock_socket(*args, **kwargs):
            raise OSError("Socket is disabled!")
        socket.socket = mock_socket
        from neon_utils.net_utils import get_ip_address

        with self.assertRaises(OSError):
            get_ip_address()

    def test_get_adapter_info(self):
        from neon_utils.net_utils import get_adapter_info
        try:
            info = get_adapter_info()
            self.assertIsInstance(info, dict)
            self.assertIsInstance(info.get("mac"), str)
            self.assertEqual(len(info["mac"]), 17)
            self.assertIsInstance(info.get("ipv4"), str)
            self.assertEqual(len(info["ipv4"].split('.')), 4)
            self.assertIsInstance(info.get("ipv6"), str)
            print(info["ipv6"])
            self.assertGreater(info["ipv6"].count(':'), 3)
        except IndexError:
            print("No Connection")

    def test_get_adapter_fail(self):
        from neon_utils.net_utils import get_adapter_info

        with self.assertRaises(IndexError):
            get_adapter_info("FAIL")

    def test_check_url_connection_valid_online(self):
        from neon_utils.net_utils import check_url_response

        self.assertTrue(check_url_response())
        self.assertTrue(check_url_response("google.com"))
        self.assertTrue(check_url_response("https://github.com"))

    def test_check_url_connection_invalid_schema(self):
        from neon_utils.net_utils import check_url_response

        with self.assertRaises(ValueError):
            check_url_response("smb://google.com")
        with self.assertRaises(ValueError):
            check_url_response("ssh://github.com")

    def test_check_url_connection_invalid_args(self):
        from neon_utils.net_utils import check_url_response

        with self.assertRaises(ValueError):
            check_url_response("")
        with self.assertRaises(ValueError):
            check_url_response(123)
        with self.assertRaises(ValueError):
            check_url_response(None)

    def test_check_url_connection_valid_offline(self):
        def mock_socket(*args, **kwargs):
            raise ConnectionError("Socket is disabled!")
        socket.socket = mock_socket
        from neon_utils.net_utils import check_url_response

        self.assertFalse(check_url_response())

    def test_check_url_connection_invalid_url(self):
        from neon_utils.net_utils import check_url_response

        self.assertFalse(check_url_response("https://api.neon.ai"))

    def test_check_online_valid_online(self):
        from neon_utils.net_utils import check_online
        self.assertTrue(check_online())
        self.assertTrue(check_online(("google.com", "github.com")))
        self.assertTrue(check_online(("api.neon.ai", "google.com")))
        self.assertTrue(check_online(("", "google.com")))

    def test_check_online_invalid_offline(self):
        from neon_utils.net_utils import check_online
        self.assertFalse(check_online(("api.neon.ai",)))
        self.assertFalse(check_online(("",)))

    def test_check_online_valid_offline(self):
        def mock_socket(*args, **kwargs):
            raise ConnectionError("Socket is disabled!")
        socket.socket = mock_socket
        from neon_utils.net_utils import check_online
        self.assertFalse(check_online())
        self.assertFalse(check_online(("google.com", "github.com")))

    def test_check_online_invalid_params(self):
        from neon_utils.net_utils import check_online
        with self.assertRaises(ValueError):
            check_online(None)
        with self.assertRaises(ValueError):
            check_online("google.com")
        with self.assertRaises(ValueError):
            check_online(123)

    def test_check_port_is_open(self):
        from neon_utils.net_utils import check_port_is_open
        self.assertTrue(check_port_is_open("api.neon.ai", 5672))
        self.assertFalse(check_port_is_open("www.neon.ai", 5672))


if __name__ == '__main__':
    unittest.main()
