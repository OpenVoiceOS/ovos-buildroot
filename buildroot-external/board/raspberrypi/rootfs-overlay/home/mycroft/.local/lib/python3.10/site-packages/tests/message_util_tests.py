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
from time import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.message_utils import *

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

VALID_STRING = 'This is only a test!'
VALID_BYTES = b'This is only a test!'
ENCODED_UTF8 = "VGhpcyBpcyBvbmx5IGEgdGVzdCE="
ENCODED_UTF16 = "䝖灨祣灂祣療浢㕸䝉杅䝤穖䍤㵅"


def get_message_standard(message):
    print(message)
    return dig_for_message()


def get_message_alt_name(msg):
    print(msg)
    return dig_for_message()


def get_message_no_name(_):
    return dig_for_message()


class MessageUtilTests(unittest.TestCase):
    def test_request_from_mobile(self):
        from_mobile = request_from_mobile(Message("", {}, {"mobile": True}))
        self.assertTrue(from_mobile)

        not_from_mobile = request_from_mobile(Message("", {}, {}))
        self.assertFalse(not_from_mobile)

    def test_get_message_username(self):
        with_user = get_message_user(Message("", {}, {"username": "testrunner"}))
        self.assertEqual(with_user, "testrunner")

        without_user = get_message_user(Message(""))
        self.assertIsNone(without_user)

    def test_get_message_username_invalid_arg(self):
        with self.assertRaises(ValueError):
            get_message_user(None)

        with self.assertRaises(AttributeError):
            get_message_user("Nobody")

    def test_encode_bytes_valid(self):
        encoded_8 = encode_bytes_to_b64_string(VALID_BYTES, 'utf-8')
        self.assertIsInstance(encoded_8, str)
        self.assertEqual(encoded_8, ENCODED_UTF8)

    def test_encode_bytes_invalid_data_type(self):
        with self.assertRaises(ValueError):
            encode_bytes_to_b64_string(ENCODED_UTF8)

    def test_encode_bytes_invalid_charset(self):
        with self.assertRaises(EncodingError):
            encode_bytes_to_b64_string(VALID_BYTES, "INVALID_ENCODING")

    def test_decode_bytes_valid(self):
        decoded_8 = decode_b64_string_to_bytes(ENCODED_UTF8, 'utf-8')
        self.assertIsInstance(decoded_8, bytes)
        self.assertEqual(decoded_8, VALID_BYTES)

    def test_decode_bytes_invalid_data_type(self):
        with self.assertRaises(ValueError):
            decode_b64_string_to_bytes(VALID_BYTES)

    def test_decode_bytes_incorrect_encoding(self):
        with self.assertRaises(EncodingError):
            decode_b64_string_to_bytes(ENCODED_UTF16, "utf-8")

    def test_decode_bytes_invalid_encoding(self):
        with self.assertRaises(EncodingError):
            decode_b64_string_to_bytes(ENCODED_UTF8, "INVALID_ENCODING")

    def test_dig_for_message_simple(self):
        test_msg = Message("test message", {"test": "data"}, {"time": time()})
        self.assertEqual(test_msg, get_message_standard(test_msg))
        test_msg = Message("test message", {"test": "data"}, {"time": time()})
        self.assertEqual(test_msg, get_message_alt_name(test_msg))
        test_msg = Message("test message", {"test": "data"}, {"time": time()})
        self.assertEqual(test_msg, get_message_no_name(test_msg))

    def test_dig_for_message_nested(self):
        message = Message("test message", {"test": "data"}, {"time": time()})

        def simple_wrapper():
            return get_message_no_name(message)

        self.assertEqual(simple_wrapper(), message)

        message = Message("test message", {"test": "data"}, {"time": time()})

        def get_message():
            return dig_for_message()

        def wrapper_method(msg):
            self.assertEqual(msg, get_message())

        wrapper_method(message)

    def test_dig_for_message_invalid_type(self):
        tester = Message("test message", {"test": "data"}, {"time": time()})

        def wrapper_method(_):
            return dig_for_message()
        self.assertIsNone(wrapper_method(dict()))

    def test_dig_for_message_no_method_call(self):
        message = Message("test message", {"test": "data"}, {"time": time()})
        self.assertIsNone(dig_for_message())

    def test_resolve_message(self):
        def wrapper_method(message, function: callable,
                           fn_args: list = None, fn_kwargs: dict = None):
            fn_args = fn_args or list()
            fn_kwargs = fn_kwargs or dict()
            function(*fn_args, **fn_kwargs)

        def nested_get_message(message=None):
            get_message_simple(message)
            get_message_multi_args("test", message)

        @resolve_message
        def get_message_simple(message=None):
            self.assertIsInstance(message, Message)
            self.assertEqual(message, test_message)

        @resolve_message
        def get_message_invalid_args(test=None):
            self.assertNotIsInstance(test, Message)

        @resolve_message
        def get_message_kwargs(*args, **kwargs):
            if args:
                self.assertIn(test_message, args)
            else:
                self.assertIsInstance(kwargs["message"], Message)
                self.assertEqual(kwargs["message"], test_message)

        @resolve_message
        def get_message_multi_args(test, message=None):
            self.assertEqual(test, "test")
            self.assertEqual(message, test_message)

        test_message = Message("test", {"data": "val"}, {"context": False})
        wrapper_method(test_message, get_message_simple)
        wrapper_method(test_message, get_message_simple, [test_message])
        wrapper_method(test_message, get_message_simple,
                       fn_kwargs={"message": test_message})

        wrapper_method(test_message, get_message_invalid_args)
        wrapper_method(test_message, get_message_invalid_args, ["test"])

        wrapper_method(test_message, get_message_kwargs)
        wrapper_method(test_message, get_message_kwargs,
                       fn_kwargs={"message": test_message})
        wrapper_method(test_message, get_message_kwargs,
                       fn_args=[test_message])

        wrapper_method(test_message, nested_get_message)

    def test_request_for_neon(self):
        from neon_utils.message_utils import request_for_neon

        minimal_message = Message("test")
        self.assertTrue(request_for_neon(minimal_message))
        self.assertFalse(request_for_neon(minimal_message, ww_enabled=False))

        neon_should_respond = Message("test", {},
                                      {"neon_should_respond": True})
        self.assertTrue(request_for_neon(neon_should_respond))
        self.assertTrue(request_for_neon(neon_should_respond,
                                         ww_enabled=False))

        neon_voc = Message("test", {"neon": "nyan"},
                           {"neon_shoud_respond": False})
        self.assertTrue(request_for_neon(neon_voc, ww_enabled=False))
        self.assertFalse(request_for_neon(neon_voc, "mycroft",
                                          ww_enabled=False))

        server_request_public = Message("test", {},
                                        {"klat_data": {"title": "title"}})
        self.assertFalse(request_for_neon(server_request_public))

        server_request_private = Message("test", {},
                                         {"klat_data": {
                                             "title": "!PRIVATE:user"}})
        self.assertTrue(request_for_neon(server_request_private))

    def test_build_message(self):
        from neon_utils.message_utils import MessageKind, build_message
        base_message = Message("test", context={"context": time()})
        speak = build_message("neon speak", "test utterance", base_message)
        self.assertEqual(speak.context['context'],
                         base_message.context['context'])

        self.assertEqual(speak.msg_type, "speak")
        self.assertEqual(speak.data, {"utterance": "test utterance",
                                      "lang": "en-US",
                                      "speaker": {
                                          "name": "Neon",
                                          "language": "en-us",
                                          "gender": "female",
                                          "voice": "",
                                          "override_user": True
                                      }})

        utt = "testing again"
        speaker = {"name": "test name",
                   "lang": "uk-ua"}
        base_message.data['lang'] = 'uk-ua'
        execute = build_message(MessageKind.EXECUTE, utt, base_message,
                                speaker)
        self.assertEqual(execute.msg_type, "skills:execute.utterance")
        self.assertEqual(execute.data["utterances"], [utt])
        self.assertEqual(execute.data["lang"], "uk-ua")
        self.assertEqual(execute.data["speaker"], speaker)
        self.assertEqual(execute.context["cc_data"],
                         {"request": utt,
                          "emit_response": True,
                          "execute_from_script": True
                          })


if __name__ == '__main__':
    unittest.main()
