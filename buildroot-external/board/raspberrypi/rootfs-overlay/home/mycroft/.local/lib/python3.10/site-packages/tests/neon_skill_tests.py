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

import datetime
import os
import shutil
import sys
import unittest
import pytest

from multiprocessing import Event
from os.path import join
from threading import Thread
from time import sleep, time
from ovos_utils.messagebus import FakeBus
from mock import Mock


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.cache_utils import LRUCache
from neon_utils.signal_utils import check_for_signal

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from skills import *

MycroftSkill = PatchedMycroftSkill
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SKILL_PATH = os.path.join(ROOT_DIR, "skills")
BUS = FakeBus()


def get_test_mycroft_skill(bus_events: dict):
    skill = MycroftSkill()
    bus = FakeBus()
    for event, callback in bus_events.items():
        bus.on(event, callback)
    bus.run_in_thread()
    if hasattr(skill, "_startup"):
        skill._startup(bus)
    else:
        skill.bind(bus)
    return skill


def get_test_neon_skill(bus_events: dict):
    skill = NeonSkill()
    bus = FakeBus()
    for event, callback in bus_events.items():
        bus.on(event, callback)
    bus.run_in_thread()
    if hasattr(skill, "_startup"):
        skill._startup(bus)
    else:
        skill.bind(bus)
    return skill


def create_skill(skill):
    skill = skill()
    if hasattr(skill, "_startup"):
        skill._startup(BUS)
    return skill


class SkillObjectTests(unittest.TestCase):
    def test_alt_fallback_skill(self):
        skill = create_skill(TestMycroftFallbackSkill)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertIsInstance(skill, FallbackSkill)

    def test_common_message_skill_init(self):
        skill = create_skill(TestCMS)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertIsInstance(skill, NeonSkill)
        self.assertIsInstance(skill, CommonMessageSkill)
        self.assertEqual(skill.name, "Test Common Message Skill")

    def test_common_play_skill_init(self):
        skill = create_skill(TestCPS)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertIsInstance(skill, NeonSkill)
        self.assertIsInstance(skill, CommonPlaySkill)
        self.assertEqual(skill.name, "Test Common Play Skill")

    def test_common_query_skill_init(self):
        skill = create_skill(TestCQS)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertIsInstance(skill, NeonSkill)
        self.assertIsInstance(skill, CommonQuerySkill)
        self.assertEqual(skill.name, "Test Common Query Skill")

    def test_fallback_skill_init(self):
        skill = create_skill(TestFBS)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertIsInstance(skill, NeonSkill)
        self.assertIsInstance(skill, NeonFallbackSkill)
        # self.assertIsInstance(skill, FallbackSkill)
        self.assertEqual(skill.name, "Test Fallback Skill")

    def test_neon_skill_init(self):
        skill = create_skill(TestNeonSkill)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertIsInstance(skill, NeonSkill)
        self.assertEqual(skill.name, "Test Neon Skill")

        self.assertIsInstance(skill.lru_cache, LRUCache)
        self.assertIsInstance(skill.sys_tz, datetime.tzinfo)
        self.assertIsInstance(skill.gui_enabled, bool)
        self.assertIsInstance(skill.neon_core, bool)
        self.assertIsInstance(skill.actions_to_confirm, dict)

        self.assertIsInstance(skill.skill_mode, str)
        self.assertIsInstance(skill.extension_time, int)

        if skill.lang_detector:
            from ovos_plugin_manager.templates.language import LanguageDetector
            self.assertIsInstance(skill.lang_detector, LanguageDetector)
        if skill.translator:
            from ovos_plugin_manager.templates.language import LanguageTranslator
            self.assertIsInstance(skill.translator, LanguageTranslator)

        self.assertIsInstance(skill.settings, dict)
        self.assertIsInstance(skill.location_timezone, str)
        self.assertIsInstance(skill.preference_skill(), dict)
        self.assertEqual(skill.settings, skill.preference_skill())
        self.assertIsInstance(skill.file_system.path, str)
        # self.assertEqual(skill.file_system.path, skill.settings_write_path)
        # self.assertNotEqual(os.path.basename(skill.file_system.path),
        #                     skill.name)

    def test_patched_mycroft_skill_init(self):
        skill = create_skill(TestPatchedSkill)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertEqual(skill.name, "Test Mycroft Skill")

        # self.assertEqual(skill.file_system.path, skill.settings_write_path)
        # self.assertNotEqual(os.path.basename(skill.file_system.path), skill.name)

    def test_instructor_skill_init(self):
        skill = create_skill(TestInstructorSkill)
        self.assertIsInstance(skill, MycroftSkill)
        self.assertEqual(skill.name, "Test Instructor Skill")


class KioskSkillTests(unittest.TestCase):
    skill = create_skill(TestKioskSkill)

    def setUp(self) -> None:
        self.skill.setup_new_interaction = Mock(return_value=True)
        self.skill.handle_new_interaction = Mock()
        self.skill.handle_end_interaction = Mock()
        self.skill.handle_user_utterance = Mock()
        self.skill.speak_dialog = Mock()
        self.skill.event_scheduler.schedule_event = Mock()

    def test_kiosk_skill_init(self):
        self.assertIsInstance(self.skill, MycroftSkill)
        self.assertIsInstance(self.skill, NeonSkill)
        self.assertEqual(self.skill.greeting_dialog, 'greeting')
        self.assertEqual(self.skill.goodbye_dialog, 'goodbye')
        self.assertEqual(self.skill.timeout_dialog, 'timeout')
        self.assertEqual(self.skill.error_dialog, 'error')

    def test_skill_timeout(self):
        test_message = Message('test', {}, {'username': 'test_user'})

        # Test Timeout
        self.skill._timeout_seconds = 1
        self.skill.start_interaction(test_message)
        self.assertEqual(set(self.skill._active_users.keys()), {'test_user'})
        self.skill.setup_new_interaction.assert_called_once_with(test_message)
        self.skill.handle_new_interaction.assert_called_once_with(test_message)
        self.skill.speak_dialog.assert_called_once_with(self.skill.greeting_dialog)
        args = self.skill.event_scheduler.schedule_event.call_args
        self.assertEqual(args[0][0], self.skill._handle_timeout)
        self.assertIsInstance(args[0][1], datetime.datetime)
        self.assertEqual(args[0][2], test_message.data)
        self.assertEqual(args[0][3], f"{self.skill.skill_id}:timeout_test_user")
        self.assertEqual(args[1]['context'], {**test_message.context,
                                              **{'skill_id': self.skill.skill_id}})
        expiration_message = Message(f'{self.skill.skill_id}:timeout_test_user',
                                     test_message.data, args[1]['context'])
        self.skill._handle_timeout(expiration_message)
        self.skill.speak_dialog.assert_called_with(self.skill.timeout_dialog)
        self.assertEqual(self.skill._active_users, dict())

    def test_skill_error_handling(self):
        test_message = Message('test', {}, {'username': 'test_user'})

        # Test error handling
        self.skill.handle_error(test_message)
        self.skill.speak_dialog.assert_called_once_with(self.skill.error_dialog,
                                                        message=test_message)

    def test_skill_setup_failure(self):
        test_message = Message('test', {}, {'username': 'test_user'})

        # Test setup failure
        self.skill.setup_new_interaction.return_value = False
        self.skill.start_interaction(test_message)
        self.skill.setup_new_interaction.assert_called_once_with(test_message)
        self.assertEqual(self.skill._active_users, dict())

    def test_skill_normal_interaction(self):
        test_message = Message('test', {}, {'username': 'test_user'})

        self.skill._timeout_seconds = 30
        self.skill.start_interaction(test_message)
        self.assertEqual(set(self.skill._active_users.keys()), {'test_user'})
        self.skill.setup_new_interaction.assert_called_once_with(test_message)
        self.skill.handle_new_interaction.assert_called_once_with(test_message)
        self.skill.speak_dialog.assert_called_once_with(self.skill.greeting_dialog)

        # Test simple converse
        sleep(1)
        converse_message = Message('converse', {}, {'username': 'test_user'})
        self.assertTrue(self.skill.converse(converse_message))
        self.skill.handle_user_utterance.assert_called_once_with(converse_message)
        self.assertAlmostEqual(self.skill._active_users['test_user'], time(), 1)

        # Test long-running converse handler
        msg = None
        event = Event()

        def _handle_utterance(message):
            nonlocal msg
            msg = message
            sleep(5)
            event.set()

        self.skill.handle_user_utterance = _handle_utterance
        self.assertTrue(self.skill.converse(converse_message))
        self.assertFalse(event.is_set())
        event.wait(5)
        finished_time = time()
        self.assertEqual(msg, converse_message)
        sleep(0.5)
        self.assertAlmostEqual(self.skill._active_users['test_user'],
                               finished_time, 1)

        # Test end interaction
        end_message = Message('end', {}, {'username': 'test_user'})
        self.skill.end_interaction(end_message)
        self.skill.handle_end_interaction.assert_called_once_with(end_message)
        self.skill.speak_dialog.assert_called_with(self.skill.goodbye_dialog)
        self.assertEqual(self.skill._active_users, dict())

    def test_skill_stop(self):
        real_converse = self.skill._handle_converse
        self.skill._handle_converse = Mock()

        test_message = Message('test', {"utterance": "stop"}, {'username': 'test_user'})

        self.skill._timeout_seconds = 30
        self.skill.start_interaction(test_message)
        self.assertEqual(set(self.skill._active_users.keys()), {'test_user'})

        self.skill.converse(test_message)
        self.skill._handle_converse.assert_not_called()
        self.assertNotIn("test_user", self.skill._active_users.keys())

        self.skill._handle_converse = real_converse


class ChatSkillTests(unittest.TestCase):
    def test_skill_init(self):
        msg: Message = None

        def handle_register(message):
            nonlocal msg
            msg = message

        BUS.once("register_chat_handler", handle_register)

        # Test decorator registration
        skill = create_skill(TestChatSkill)
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data['name'], "Test Bot")
        self.assertEqual(msg.context['skill_id'], skill.skill_id)

        # Test decorated method
        test_message = Message("chat.Test Bot", {"test_response": "nothing"},
                               {'test': True})
        resp = BUS.wait_for_response(test_message)
        self.assertEqual(resp.msg_type, f'{test_message.msg_type}.response')
        self.assertEqual(resp.data,
                         {'response': test_message.data['test_response']})
        self.assertEqual(resp.context, {'test': True,
                                        'skill_id': skill.skill_id})


class PatchedMycroftSkillTests(unittest.TestCase):
    def test_get_response_simple(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog)
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response."
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["testing one", "testing 1",
                                          "resting one"]},
                          {"timing": {},
                           "username": "local"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, message.context["username"]), daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(message)
        t.join(5)
        self.assertEqual(test_results[message.context["username"]],
                         message.data["utterances"][0])

    def test_get_response_interrupt_prompt(self):
        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog)
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response."
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["testing one", "testing 1",
                                          "resting one"]},
                          {"timing": {},
                           "username": "local"})

        skill = get_test_mycroft_skill({})
        t = Thread(target=skill_response_thread,
                   args=(skill, message.context["username"]), daemon=True)
        t.start()
        sleep(1)
        skill.converse(message)
        t.join(5)
        self.assertEqual(test_results[message.context["username"]],
                         message.data["utterances"][0])

    def test_get_response_no_username(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog)
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response."
        message = Message("recognizer_loop:utterance",
                          {"utterances": ["testing one", "testing 1",
                                          "resting one"]},
                          {"timing": {}})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread, args=(skill, "0"),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(message)
        t.join(5)
        self.assertEqual(test_results["0"], message.data["utterances"][0])

    def test_get_response_multi_user(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, message=Message(
                "converse_message", {}, {"username": "valid_converse_user"}))
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["testing one",
                                                "testing 1", "resting one"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})
        invalid_message = Message("recognizer_loop:utterance",
                                  {"utterances": ["invalid return"]},
                                  {"timing": {},
                                   "username": "invalid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(invalid_message)
        skill.converse(valid_message)
        skill.converse(invalid_message)
        t.join(5)
        self.assertEqual(test_results[valid_message.context["username"]],
                         valid_message.data["utterances"][0])

    def test_get_response_dig_for_message(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def skill_response_thread(s: MycroftSkill, idx: str):
            def intent_handler(message):
                resp = s.get_response(test_dialog)
                test_results[idx] = resp
            intent_handler(Message("converse_message",
                                   {}, {"username": "valid_converse_user"}))

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["testing one", "testing 1",
                                                "resting one"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})
        invalid_message = Message("recognizer_loop:utterance",
                                  {"utterances": ["invalid return"]},
                                  {"timing": {},
                                   "username": "invalid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(invalid_message)
        skill.converse(valid_message)
        skill.converse(invalid_message)
        t.join(5)
        self.assertEqual(test_results[valid_message.context["username"]],
                         valid_message.data["utterances"][0])

    def test_get_response_no_response(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, num_retries=0, message=Message(
                "converse_message", {}, {"username": "valid_converse_user"}))
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["testing one", "testing 1",
                                                "resting one"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})
        invalid_message = Message("recognizer_loop:utterance",
                                  {"utterances": ["invalid return"]},
                                  {"timing": {},
                                   "username": "invalid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        skill._get_response_timeout = 5
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        self.assertTrue(spoken.wait(30))
        sleep(1)
        skill.converse(invalid_message)
        t.join(30)
        self.assertIsNone(test_results[valid_message.context["username"]])

    def test_get_response_validator_return_utterance(self):
        # returns utterance if validotor return value is True
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def is_valid(_):
            test_results["validator"] = True
            return True

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, validator=is_valid,
                                  message=Message(
                                      "converse_message", {},
                                      {"username": "valid_converse_user"}))
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["testing one", "testing 1",
                                                "resting one"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(valid_message)
        t.join(30)
        self.assertTrue(test_results["validator"])
        self.assertEqual(test_results[valid_message.context["username"]],
                         valid_message.data["utterances"][0])

    def test_get_response_validator_return_value_1(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def is_valid(_):
            test_results["validator"] = True
            return valid_return

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, validator=is_valid,
                                  message=Message(
                                      "converse_message", {},
                                      {"username": "valid_converse_user"}))
            test_results[idx] = resp

        test_results = dict()
        valid_return = datetime.datetime(2022,11,29,0,0)
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["today"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(valid_message)
        t.join(30)
        self.assertTrue(test_results["validator"])
        self.assertEqual(test_results[valid_message.context["username"]],
                         valid_return)

    def test_get_response_validator_return_value_2(self):
        # validator should also accept faulty values that ar not None/False
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def is_valid(_):
            test_results["validator"] = True
            return valid_return

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, validator=is_valid,
                                  message=Message(
                                      "converse_message", {},
                                      {"username": "valid_converse_user"}))
            test_results[idx] = resp

        test_results = dict()
        valid_return = 0
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["got zero items"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(valid_message)
        t.join(30)
        self.assertTrue(test_results["validator"])
        self.assertEqual(test_results[valid_message.context["username"]],
                         valid_return)

    def test_get_response_validator_fail(self):
        def handle_speak(_):
            check_for_signal("isSpeaking")
            spoken.set()

        def is_valid(_):
            test_results["validator"] = True
            return False

        on_fail = Mock()

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, validator=is_valid,
                                  on_fail=on_fail, message=Message(
                    "converse_message", {},
                    {"username": "valid_converse_user"}))
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["testing one", "testing 1",
                                                "resting one"]},
                                {"timing": {},
                                 "username": "valid_converse_user"})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        sleep(1)
        skill.converse(valid_message)
        t.join(30)
        self.assertTrue(test_results["validator"])
        on_fail.assert_called_once()
        on_fail.assert_called_with("testing one")

    def test_get_response_klat(self):
        speak_message: Message = None
        def handle_speak(msg):
            nonlocal speak_message
            speak_message = msg
            spoken.set()

        def skill_response_thread(s: MycroftSkill, idx: str):
            resp = s.get_response(test_dialog, message=Message(
                "converse_message", {},
                {"username": "valid_converse_user",
                 "klat_data": {"title": "Public Convo"}}))
            test_results[idx] = resp

        test_results = dict()
        spoken = Event()
        test_dialog = "testing get response multi user."
        valid_message = Message("recognizer_loop:utterance",
                                {"utterances": ["testing one",
                                                "testing 1", "resting one"]},
                                {"timing": {},
                                 "username": "valid_converse_user",
                                 "klat_data": {"title": "Public Convo"}})
        invalid_message = Message("recognizer_loop:utterance",
                                  {"utterances": ["invalid return"]},
                                  {"timing": {},
                                   "username": "invalid_converse_user",
                                   "klat_data": {"title": "Public Convo"}})

        skill = get_test_mycroft_skill({"speak": handle_speak})
        t = Thread(target=skill_response_thread,
                   args=(skill, valid_message.context["username"]),
                   daemon=True)
        t.start()
        spoken.wait(30)
        self.assertIsInstance(speak_message, Message)
        self.assertTrue(speak_message.data['utterance'].startswith('@valid_converse_user '),
                        speak_message.data['utterance'])
        sleep(1)
        skill.converse(invalid_message)
        skill.converse(valid_message)
        skill.converse(invalid_message)
        t.join(5)
        self.assertEqual(test_results[valid_message.context["username"]],
                         valid_message.data["utterances"][0])

# TODO: test get_response with `speak_bus_api`

    def test_speak_simple_valid(self):
        handle_speak = Mock()
        utterance = "test to speak"
        skill = get_test_mycroft_skill({"speak": handle_speak})
        skill.speak(utterance)
        handle_speak.assert_called_once()
        msg = handle_speak.call_args.args[0]
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data["utterance"], utterance)
        self.assertEqual(msg.data["expect_response"], False)
        self.assertIsInstance(msg.data["meta"], dict)
        self.assertIsNone(msg.data["speaker"])
        self.assertEqual(msg.context['destination'], ['audio'])
        self.assertEqual(msg.context['source'], ['skills'])

    def test_speak_speaker_valid(self):
        handle_speak = Mock()
        utterance = "test to speak"
        speaker = {"speaker": "Test Speaker",
                   "language": "en-au",
                   "gender": "female"}
        skill = get_test_mycroft_skill({"speak": handle_speak})
        skill.speak(utterance, speaker=speaker)
        handle_speak.assert_called_once()
        msg = handle_speak.call_args.args[0]
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data["utterance"], utterance)
        self.assertEqual(msg.data["expect_response"], False)
        self.assertIsInstance(msg.data["meta"], dict)
        self.assertEqual(msg.data["speaker"], speaker)
        self.assertEqual(msg.context['destination'], ['audio'])
        self.assertEqual(msg.context['source'], ['skills'])

    def test_speak_simple_with_message_valid(self):
        message = Message("date-time.neon:handle_query_time",
                          {'intent_type': 'date-time.neon:handle_query_time',
                           'target': None,
                           'confidence': 0.6666666666666666,
                           'utterance': 'what time is it neon'},
                          {'client_name': 'mycroft_cli',
                           'source': ['skills'],
                           'destination': 'debug_cli',
                           'client': 'local',
                           'neon_should_respond': False,
                           'timing': {'transcribed': 1631062887.5719671,
                                      'text_parsers': 0.34954047203063965,
                                      'speech_start': 1631062888.1001909},
                           'audio_file': '',
                           'skill_id': 'date-time.neon'})
        handle_speak = Mock()
        utterance = "test to speak"
        skill = get_test_mycroft_skill({"speak": handle_speak})
        skill.speak(utterance, message=message)
        handle_speak.assert_called_once()
        msg = handle_speak.call_args.args[0]
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data["utterance"], utterance)
        self.assertEqual(msg.data["expect_response"], False)
        self.assertIsInstance(msg.data["meta"], dict)
        self.assertIsNone(msg.data["speaker"])
        self.assertEqual(msg.context.pop('destination'), ['audio'])
        self.assertEqual(msg.context.pop('source'), ['skills'])
        message.context.pop('source')
        message.context.pop('destination')
        self.assertEqual(message.context, msg.context)

    def test_speak_speaker_with_message_override_valid(self):
        message = Message("date-time.neon:handle_query_time",
                          {'intent_type': 'date-time.neon:handle_query_time',
                           'target': None,
                           'confidence': 0.6666666666666666,
                           'utterance': 'what time is it neon',
                           'speaker': {"speaker": "invalid speaker",
                                       "language": "es-es"}},
                          {'client_name': 'mycroft_cli',
                           'source': ['skills'],
                           'destination': 'debug_cli',
                           'client': 'local',
                           'neon_should_respond': False,
                           'timing': {'transcribed': 1631062887.5719671,
                                      'text_parsers': 0.34954047203063965,
                                      'speech_start': 1631062888.1001909},
                           'audio_file': '',
                           'skill_id': 'date-time.neon'})
        handle_speak = Mock()
        utterance = "test to speak"
        speaker = {"speaker": "Test Speaker",
                   "language": "en-au",
                   "gender": "female"}
        skill = get_test_mycroft_skill({"speak": handle_speak})
        skill.speak(utterance, speaker=speaker, message=message)
        handle_speak.assert_called_once()
        msg = handle_speak.call_args.args[0]
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data["utterance"], utterance)
        self.assertEqual(msg.data["expect_response"], False)
        self.assertIsInstance(msg.data["meta"], dict)
        self.assertEqual(msg.data["speaker"], speaker)
        self.assertEqual(msg.context.pop('destination'), ['audio'])
        self.assertEqual(msg.context.pop('source'), ['skills'])
        message.context.pop('source')
        message.context.pop('destination')
        self.assertEqual(message.context, msg.context)

    def test_speak_speaker_with_message_valid(self):
        speaker = {"speaker": "Test Speaker",
                   "language": "en-au",
                   "gender": "female"}
        message = Message("date-time.neon:handle_query_time",
                          {'intent_type': 'date-time.neon:handle_query_time',
                           'target': None,
                           'confidence': 0.6666666666666666,
                           'utterance': 'what time is it neon',
                           'speaker': speaker},
                          {'client_name': 'mycroft_cli',
                           'source': ['skills'],
                           'destination': 'debug_cli',
                           'client': 'local',
                           'neon_should_respond': False,
                           'timing': {'transcribed': 1631062887.5719671,
                                      'text_parsers': 0.34954047203063965,
                                      'speech_start': 1631062888.1001909},
                           'audio_file': '',
                           'skill_id': 'date-time.neon'})
        handle_speak = Mock()
        utterance = "test to speak"

        skill = get_test_mycroft_skill({"speak": handle_speak})
        skill.speak(utterance, message=message)
        handle_speak.assert_called_once()
        msg = handle_speak.call_args.args[0]
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data["utterance"], utterance)
        self.assertEqual(msg.data["expect_response"], False)
        self.assertIsInstance(msg.data["meta"], dict)
        self.assertEqual(msg.data["speaker"], speaker)
        self.assertEqual(msg.context.pop('destination'), ['audio'])
        self.assertEqual(msg.context.pop('source'), ['skills'])
        message.context.pop('source')
        message.context.pop('destination')
        self.assertEqual(message.context, msg.context)

    def test_speak_emit_response_valid(self):
        message = Message("date-time.neon:handle_query_time",
                          {'intent_type': 'date-time.neon:handle_query_time',
                           'target': None,
                           'confidence': 0.6666666666666666,
                           'utterance': 'what time is it neon'},
                          {'client_name': 'mycroft_cli',
                           'source': ['skills'],
                           'destination': 'debug_cli',
                           'client': 'local',
                           'neon_should_respond': False,
                           'timing': {'transcribed': 1631062887.5719671,
                                      'text_parsers': 0.34954047203063965,
                                      'speech_start': 1631062888.1001909},
                           'audio_file': '',
                           'skill_id': 'date-time.neon',
                           "cc_data": {"emit_response": True}})
        handle_execute_response = Mock()
        utterance = "test to speak"

        skill = get_test_mycroft_skill(
            {"skills:execute.response": handle_execute_response})
        skill.speak(utterance, message=message)
        handle_execute_response.assert_called_once()
        msg = handle_execute_response.call_args.args[0]
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.data["utterance"], utterance)
        self.assertEqual(msg.data["expect_response"], False)
        self.assertIsInstance(msg.data["meta"], dict)
        self.assertEqual(msg.context.pop('destination'), ['skills'])
        self.assertEqual(msg.context.pop('source'), ['skills'])
        message.context.pop('source')
        message.context.pop('destination')
        self.assertEqual(message.context, msg.context)

    def test_speak_wait(self):
        from neon_utils.signal_utils import create_signal, check_for_signal, \
            wait_for_signal_clear
        create_signal("neon_speak_api")
        message: Message = None

        def on_speak(msg):
            def handler(msg):
                nonlocal message
                message = msg
                sleep(1)
                skill.bus.emit(Message(msg.data.get('speak_ident')))
                sleep(1)
                check_for_signal("isSpeaking")
            Thread(target=handler, args=(msg,), daemon=True).start()

        skill = get_test_mycroft_skill(
            {"speak": on_speak})

        # Test wait with speak API
        speak_time = time()
        create_signal("isSpeaking")  # Mock signal create
        skill.speak('test', wait=True)
        # Make sure we actually waited
        self.assertGreaterEqual(time(), speak_time + 1)
        self.assertLessEqual(time(), speak_time + 2)
        self.assertTrue(check_for_signal("neon_speak_api", -1))
        self.assertIsInstance(message, Message)
        self.assertIsInstance(message.data['speak_ident'], str)

        wait_for_signal_clear('isSpeaking')  # Wait for first test to finish
        # Test wait with signals
        self.assertTrue(check_for_signal("neon_speak_api"))
        speak_time = time()
        create_signal("isSpeaking")  # Mock signal create
        skill.speak('test', wait=True)
        # Make sure we actually waited
        self.assertGreaterEqual(time(), speak_time + 2)
        self.assertFalse(check_for_signal("neon_speak_api", -1))

    # TODO: Test settings load


class NeonSkillTests(unittest.TestCase):
    skill = None
    config_dir = os.path.join(os.path.dirname(__file__), "skills", "config")

    @classmethod
    def setUpClass(cls) -> None:
        from skills.test_skill import TestSkill

        bus = FakeBus()
        os.environ["XDG_CONFIG_HOME"] = cls.config_dir
        cls.skill = TestSkill()
        # Mock the skill_loader process
        if hasattr(cls.skill, "_startup"):
            cls.skill._startup(bus)
        else:
            cls.skill.bind(bus)
            cls.skill.load_data_files()
            cls.skill.initialize()

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isdir(cls.config_dir):
            shutil.rmtree(cls.config_dir)
        os.environ.pop("XDG_CONFIG_HOME")

    def test_00_skill_init(self):
        self.assertIsInstance(self.skill.cache_loc, str)
        self.assertTrue(os.path.isdir(self.skill.cache_loc))
        self.assertIsNotNone(self.skill.lru_cache)
        self.assertIsInstance(self.skill.sys_tz, datetime.tzinfo)
        self.assertIsInstance(self.skill.neon_core, bool)
        self.assertIsInstance(self.skill.skill_mode, str)
        self.assertIsInstance(self.skill.extension_time, int)
        self.assertIsNotNone(self.skill.lang_detector)
        self.assertIsNotNone(self.skill.translator)

    def test_properties(self):
        self.assertIsInstance(self.skill.gui_enabled, bool)
        self.assertIsInstance(self.skill.ngi_settings, dict)
        self.assertEqual(self.skill.ngi_settings, self.skill.settings)

    def test_preference_skill(self):
        self.assertIsInstance(self.skill.preference_skill(), dict)
        self.assertEqual(self.skill.preference_skill()["boolean_type"], False)
        self.assertEqual(self.skill.preference_skill()["number_type"], 2.0)
        self.assertEqual(self.skill.preference_skill()["text_type"], "8")
        self.skill.settings['text_type'] = 'test'
        self.assertEqual(self.skill.preference_skill()["text_type"], "test")
        self.skill.settings['new_setting'] = 'test'
        self.assertEqual(self.skill.preference_skill()["new_setting"], "test")

    def test_update_profile(self):
        from neon_utils.configuration_utils import get_neon_user_config
        test_config_path = os.path.dirname(__file__)
        profile_settings = get_neon_user_config(test_config_path)
        test_username = "tester"
        profile_settings['user']['username'] = test_username
        test_message_old = Message("", {},
                                   {'username': test_username,
                                    'nick_profiles': {
                                        test_username: profile_settings.content}})
        test_message_new = Message("", {},
                                   {'username': test_username,
                                    'user_profiles': [profile_settings.content]})
        new_email = "new@email.test"
        self.skill.update_profile({'user': {'email': new_email}},
                                  test_message_old)
        self.assertEqual(test_message_old.context['nick_profiles']
                         [test_username]['user']['email'], new_email)

        self.skill.update_profile({'user': {'email': new_email}},
                                  test_message_new)
        self.assertEqual(test_message_new.context['user_profiles']
                         [0]['user']['email'], new_email)
        os.remove(profile_settings.file_path)
        # TODO: Define and test persistent data

    def test_update_skill_settings(self):
        self.skill.server = False
        settings = self.skill.settings
        self.skill.update_skill_settings(
            {"boolean_type": settings.get("boolean_type")})
        self.assertEqual(settings, self.skill.settings)

        test_val = "updated value test"
        self.skill.update_skill_settings({"text_type": test_val})
        self.assertEqual(self.skill.settings['text_type'], test_val)

        self.skill.update_skill_settings({"text_type": test_val,
                                          "new_pref": True})
        self.assertTrue(self.skill.settings['new_pref'])
        # TODO: Define and test for user-specific settings

    def test_neon_must_respond(self):
        self.assertFalse(self.skill.neon_must_respond())
        private_message_solo = Message("", {},
                                       {"klat_data": {
                                           "title": "!PRIVATE:user"}})
        private_message_neon = Message("", {},
                                       {"klat_data": {
                                           "title": "!PRIVATE:user,Neon"}})
        private_message_neon_plus = Message("", {},
                                            {"klat_data": {
                                                "title": "!PRIVATE:user,Neon,user1"}})
        public_message = Message("", {},
                                 {"klat_data": {
                                     "title": "Test Conversation"}})
        first_message = Message("",
                                {"utterance": "Welcome to your private conversation with Neon"},
                                {"klat_data": {
                                    "title": "!PRIVATE:user"}})
        self.assertFalse(self.skill.neon_must_respond())
        self.assertTrue(self.skill.neon_must_respond(private_message_solo))
        self.assertTrue(self.skill.neon_must_respond(private_message_neon))
        self.assertFalse(self.skill.neon_must_respond(private_message_neon_plus))
        self.assertFalse(self.skill.neon_must_respond(public_message))
        self.assertFalse(self.skill.neon_must_respond(first_message))

    def test_neon_in_request(self):
        # TODO: Mock `is_neon_core` and test `skill.neon_in_request` directly
        from neon_utils.message_utils import request_for_neon

        # Test message context/vocab
        neon_should_respond = Message("test_neon_should_respond", {},
                                      {'neon_should_respond': True})
        self.assertTrue(request_for_neon(neon_should_respond, "neon",
                                         self.skill.voc_match, False))

        neon_in_data = Message("test_neon_should_respond", {'neon': "Neon"},
                               {'neon_should_respond': False})
        self.assertTrue(request_for_neon(neon_in_data, "neon",
                                         self.skill.voc_match, False))

        # Test Config WW state
        self.assertFalse(request_for_neon(Message("test"), "neon",
                                          self.skill.voc_match, False))
        self.assertTrue(request_for_neon(Message("test"), "neon",
                                         self.skill.voc_match, True))

        # Test vocab match
        neon_in_utterance = Message("test_neon_in_utterance",
                                    {'utterance': "hello Neon"},
                                    {"neon_should_respond": False})
        self.assertTrue(request_for_neon(neon_in_utterance, "neon",
                                         self.skill.voc_match, False))

    def test_report_metric(self):
        metric_handler = Mock()
        self.skill.bus.on("neon.metric", metric_handler)
        self.skill.report_metric("test metric", {"name": "invalid name",
                                                 "param": "value",
                                                 "test": True})
        metric_handler.assert_called_once()
        message = metric_handler.call_args[0][0]
        self.assertEqual(message.msg_type, "neon.metric")
        self.assertEqual(message.data, {"name": "test metric",
                                        "param": "value",
                                        "test": True})

    @pytest.mark.skip
    def test_send_email(self):
        self.assertTrue(self.skill.send_email(
            "Test Message",
            "This is a test\ncalled from neon_skill_tests.py in neon-utils",
            email_addr="test@neongecko.com"))

    def test_make_active(self):
        active_request = Mock()
        self.skill.bus.on("active_skill_request", active_request)
        self.skill.make_active(15)
        active_request.assert_called_once()
        message = active_request.call_args[0][0]
        self.assertEqual(message.msg_type, "active_skill_request")
        self.assertEqual(message.data, {"skill_id": self.skill.skill_id,
                                        "timeout": 15})

    def test_request_check_timeout(self):
        set_timeout = Mock()
        self.skill.bus.on("set_timeout", set_timeout)

        self.skill.request_check_timeout(10, "timeout.intent")
        set_timeout.assert_called_once()
        message = set_timeout.call_args[0][0]
        self.assertEqual(message.msg_type, "set_timeout")
        self.assertEqual(message.data,
                         {"time_out": 10,
                          "intent_to_check":
                              f"{self.skill.skill_id}:timeout.intent"})

        set_timeout.reset_mock()
        self.skill.request_check_timeout(30, ["test_intent_1", f"test_intent"])
        self.assertEqual(set_timeout.call_count, 2)

    def test_decorate_api_call_use_lru(self):
        # TODO
        pass


class SkillGuiTests(unittest.TestCase):
    from neon_utils.skills.skill_gui import SkillGUI
    skill = get_test_neon_skill({})
    skill_gui = SkillGUI(skill)

    @classmethod
    def setUpClass(cls) -> None:

        cls.skill_gui.config = {
            "remote-server": None
        }

    def test_pages2uri(self):
        def _find_resource(*args, **kwargs):
            return join("skill_id", args[1], args[0])

        real_method = self.skill.find_resource
        self.skill.find_resource = _find_resource

        self.skill_gui.serving_http = False
        urls = self.skill_gui._pages2uri(["test_page1", "test_page2"])
        self.assertEqual(urls, ["file://skill_id/ui/test_page1",
                                "file://skill_id/ui/test_page2"])

        self.skill_gui.config = {
            "remote-server": "remote_url"
        }
        urls = self.skill_gui._pages2uri(["test_page1", "test_page2"])
        self.assertEqual(urls, ["remote_url/skill_id/ui/test_page1",
                                "remote_url/skill_id/ui/test_page2"])

        self.skill_gui.serving_http = True
        urls = self.skill_gui._pages2uri(["SYSTEM_Test1", "SYSTEM_Test2"])
        self.assertEqual(urls, ["file://remote_url/system/ui/SYSTEM_Test1",
                                "file://remote_url/system/ui/SYSTEM_Test2"])

        urls = self.skill_gui._pages2uri(["test_page1", "test_page2"])
        self.assertEqual(urls, ["file://remote_url/skills/skill_id/ui/test_page1",
                                "file://remote_url/skills/skill_id/ui/test_page2"])

        self.skill.find_resource = real_method


if __name__ == '__main__':
    unittest.main()
