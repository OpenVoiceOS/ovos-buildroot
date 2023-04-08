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

from abc import abstractmethod
from threading import Thread
from time import time
from mycroft_bus_client import Message
from ovos_utils.log import LOG

from neon_utils.message_utils import get_message_user, dig_for_message
from neon_utils.skills.neon_skill import NeonSkill


class KioskSkill(NeonSkill):
    def __init__(self, *args, **kwargs):
        NeonSkill.__init__(self, *args, **kwargs)
        self._active_users = dict()

    @property
    def timeout_seconds(self) -> int:
        """
        Time in seconds to wait for a user response before timing out
        """
        return 60

    @property
    @abstractmethod
    def greeting_dialog(self) -> str:
        """
        Specify a dialog to speak on interaction start
        """

    @property
    @abstractmethod
    def goodbye_dialog(self) -> str:
        """
        Specify a dialog to speak when an interaction ends cleanly
        """

    @property
    @abstractmethod
    def timeout_dialog(self) -> str:
        """
        Specify a dialog to speak when an interaction ends after some timeout
        """

    @property
    @abstractmethod
    def error_dialog(self) -> str:
        """
        Specify a dialog to speak on unhandled errors
        """

    def start_interaction(self, message: Message):
        """
        Start an interaction session. This may be triggered by intent,
        proximity, button press, etc.
        :param message: Message associated with request
        """
        if self.setup_new_interaction(message):
            user = get_message_user(message)
            self.speak_dialog(self.greeting_dialog)
            self._active_users[user] = time()
            self.handle_new_interaction(message)
            self._active_users[user] = time()
            self._timeout_timer(message)

    @abstractmethod
    def setup_new_interaction(self, message: Message) -> bool:
        """
        Override to include skill-specific actions on first user interaction.
        This is the first action that could prompt user to input language, etc.
        :param message: Message associated with start request
        :returns: True if user interaction is supported
        """
        return True

    @abstractmethod
    def handle_new_interaction(self, message: Message):
        """
        Override to interact with the user after the greeting message has been
        spoken.
        :param message: Message associated with start request
        """
        pass

    def end_interaction(self, message: Message):
        """
        Handle ending an interaction session. This is called if a user requests
        'stop' or if the skill decides to end interaction.
        :param message: Message associated with request
        """
        self.handle_end_interaction(message)
        self.speak_dialog(self.goodbye_dialog)
        user = get_message_user(message)
        self._active_users.pop(user)
        self.cancel_scheduled_event(f'{self.skill_id}:timeout_{user}')

    @abstractmethod
    def handle_end_interaction(self, message: Message):
        """
        Override to do any skill-specific cleanup when a user interaction is
        completed.
        :param message: Message associated with request triggering end
        """
        pass

    @abstractmethod
    def handle_user_utterance(self, message: Message):
        """
        Handle any input from a user interacting with the kiosk.
        :param message: Message associated with user utterance
        """
        self.handle_error(message)

    def handle_error(self, message: Message):
        """
        Error handler to speak a custom dialog file when an error occurs during
        user interaction.
        """
        self.speak_dialog(self.error_dialog, message=message)

    def converse(self, message: Message = None):
        user = get_message_user(message)
        if user in self._active_users:
            if self.voc_match(message.data.get('utterance'), 'stop'):
                self.bus.emit(message.forward("mycroft.stop"))
                return True
            LOG.debug(f"Consuming utterance from {user}")
            Thread(target=self._handle_converse, args=(message,),
                   daemon=True).start()
            return True
        return False

    def _handle_converse(self, message: Message):
        """
        Handle actual converse interaction in a thread so the skills service can
        get a `handled` response immediately
        """
        user = get_message_user(message)
        self.handle_user_utterance(message)
        self._active_users[user] = time()
        self._timeout_timer(message)

    def _timeout_timer(self, message: Message):
        """
        Schedule some event to handle no response from a particular user
        """
        user = get_message_user(message)
        timeout_time = datetime.datetime.fromtimestamp(
            self._active_users[user]) + \
            datetime.timedelta(seconds=self.timeout_seconds)
        event_name = f'{self.skill_id}:timeout_{user}'
        self.schedule_event(self._handle_timeout, timeout_time, message.data,
                            event_name, message.context)

    def _handle_timeout(self, message):
        """
        Handler for when a user hasn't responded within the specified timeout
        """
        user = get_message_user(message)
        if user in self._active_users:
            LOG.info(f"Response timeout for: {user}")
            self._active_users.pop(user)
            if self.timeout_dialog:
                self.speak_dialog(self.timeout_dialog)

    def stop(self):
        message = dig_for_message()
        user = get_message_user(message) if message else "local"
        if user in self._active_users:
            self.end_interaction(message)

    def _on_event_error(self, error, message, handler_info,
                        skill_data, speak_errors):
        """
        Override error handling to speak custom exception for active sessions
        """
        user = get_message_user(message)
        if user in self._active_users:
            LOG.exception(error)
            self.handle_error(message)
        else:
            super()._on_event_error(error, message, handler_info,
                                    skill_data, speak_errors)
