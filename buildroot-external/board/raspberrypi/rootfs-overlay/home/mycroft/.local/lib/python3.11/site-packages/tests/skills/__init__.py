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

from mycroft_bus_client import Message

from neon_utils.skills import CommonMessageSkill, CommonPlaySkill,\
    CommonQuerySkill, NeonFallbackSkill, NeonSkill, PatchedMycroftSkill,\
    InstructorSkill, KioskSkill

import importlib
import mycroft.skills
mycroft.skills.mycroft_skill.MycroftSkill = PatchedMycroftSkill
importlib.reload(mycroft.skills.fallback_skill)
from mycroft.skills.fallback_skill import FallbackSkill


class TestCMS(CommonMessageSkill):
    def __init__(self):
        super(TestCMS, self).__init__(name="Test Common Message Skill")

    def CMS_match_message_phrase(self, request, context):
        pass

    def CMS_handle_send_message(self, message):
        pass

    def CMS_match_call_phrase(self, contact, context):
        pass

    def CMS_handle_place_call(self, message):
        pass


class TestCPS(CommonPlaySkill):
    def __init__(self):
        super(TestCPS, self).__init__(name="Test Common Play Skill")

    def CPS_match_query_phrase(self, phrase, message):
        pass

    def CPS_start(self, phrase, data, message=None):
        pass


class TestCQS(CommonQuerySkill):
    def __init__(self):
        super(TestCQS, self).__init__(name="Test Common Query Skill")

    def CQS_match_query_phrase(self, phrase, message):
        pass


class TestFBS(NeonFallbackSkill):
    def __init__(self):
        super(TestFBS, self).__init__(name="Test Fallback Skill")


class TestNeonSkill(NeonSkill):
    def __init__(self):
        super(TestNeonSkill, self).__init__(name="Test Neon Skill")


class TestPatchedSkill(PatchedMycroftSkill):
    def __init__(self):
        super(TestPatchedSkill, self).__init__(name="Test Mycroft Skill")


class TestInstructorSkill(InstructorSkill):
    def __init__(self):
        super(TestInstructorSkill, self).__init__(name="Test Instructor Skill")

    def _access_data_source(self, *args, **kwargs):
        pass

    def _search_in_data_source(self, *args, **kwargs):
        pass

    def _get_instructions(self, *args, **kwargs):
        pass


class TestMycroftFallbackSkill(FallbackSkill):
    """
    Test case for the Mycroft HomeAssistantSkill
    """
    def __init__(self):
        from neon_utils.skills.mycroft_skill import PatchedMycroftSkill as MycroftSkill
        MycroftSkill.__init__(self)
        super().__init__(name="TestSkill")


class TestChatSkill(NeonSkill):
    from neon_utils.skills import chat_handler

    def __init__(self):
        super().__init__(name="Test Neon Chat Skill")

    @chat_handler("Test Bot")
    def handle_chat_message(self, message: Message):
        return message.data.get("test_response")


class TestKioskSkill(KioskSkill):
    def __init__(self):
        super(TestKioskSkill, self).__init__()
        self._timeout_seconds = 60

    @property
    def timeout_seconds(self) -> int:
        return self._timeout_seconds

    @property
    def greeting_dialog(self) -> str:
        return "greeting"

    @property
    def goodbye_dialog(self) -> str:
        return "goodbye"

    @property
    def timeout_dialog(self) -> str:
        return "timeout"

    @property
    def error_dialog(self) -> str:
        return "error"

    def setup_new_interaction(self, message: Message) -> bool:
        pass

    def handle_new_interaction(self, message: Message):
        pass

    def handle_end_interaction(self, message: Message):
        pass

    def handle_user_utterance(self, message: Message):
        pass
