# Copyright 2017, Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from adapt.intent import IntentBuilder
from mycroft import intent_handler
from mycroft.audio import wait_while_speaking
from mycroft.configuration.config import Configuration
from mycroft.messagebus.message import Message
from ovos_workshop.skills import OVOSSkill


class NapTimeSkill(OVOSSkill):
    """Skill to handle mycroft speech client listener sleeping."""

    def initialize(self):
        self.started_by_skill = False
        self.sleeping = False
        self.old_brightness = 30
        self.add_event('mycroft.awoken', self.handle_awoken)
        self.add_event('mycroft.awoken', self.mark1_wake_up_animation)
        self.add_event('recognizer_loop:sleep', self.mark1_sleep_animation)
        self.add_event('mycroft.awoken', self.display_waking_face)
        self.add_event('recognizer_loop:sleep', self.display_sleep_face)
        self.disabled_confirm_listening = False

    @property
    def wake_word(self):
        default = Configuration.get().get('listener', {}).get('wake_word')
        # with multiple wakewords we can't be 100% sure what the correct name is
        # a device might have multiple names
        # - if the wake_word is set in listener consider that the main wakeword
        # - if the wake_word in listener config does not have a ww config ignore it
        # - else use the first hotword that listens and is set to self.lang, assume config is ordered by priority
        # - else use the first hotword that listens, assume config is ordered by priority

        hotwords = Configuration.get().get('hotwords', {})
        if default in hotwords:
            return default

        # gather hotwords that trigger listening
        candidates = {}
        for ww_name, ww_conf in hotwords.items():
            if ww_conf.get("listen"):
                candidates[ww_name] = ww_conf

        if candidates:
            # preference to main language
            for ww_name, ww_conf in candidates.items():
                if ww_conf.get("lang", "") == self.lang:
                    return ww_name
            # assume ordered by preference in config
            return candidates[0]
        return default

    # TODO move mark1 handlers to PHAL mk1 plugin
    def mark1_sleep_animation(self, message=None):
        time.sleep(0.5)
        wait_while_speaking()
        # Dim and look downward to 'go to sleep'
        # TODO: Get current brightness from somewhere
        self.old_brightness = 30
        for i in range(0, (self.old_brightness - 10) // 2):
            self.enclosure.eyes_brightness(self.old_brightness - i * 2)
            time.sleep(0.15)
        self.enclosure.eyes_look("d")

    def mark1_wake_up_animation(self, message=None):
        """Mild animation to come out of sleep from voice command.

        Pop open eyes and wait a sec.
        """
        self.enclosure.eyes_reset()
        time.sleep(1)
        self.enclosure.eyes_blink('b')
        time.sleep(1)
        # brighten the rest of the way
        self.enclosure.eyes_brightness(self.old_brightness)

    # GUI integration
    def display_sleep_face(self) -> None:
        """Display the sleeping face depending on the platform."""
        self.gui.show_page("resting.qml", override_idle=True)

    def display_waking_face(self) -> None:
        """Display the waking face depending on the platform."""
        self.gui.remove_page("resting.qml")
        self.gui.show_page("awake.qml", override_idle=5)
        # TODO Screen not reverting after the specified 5 seconds.
        # The following 2 lines shouldn't be needed. Remove when fixed.
        time.sleep(5)
        self.gui.release()

    # TODO notifications api not yet merged
    # merge this into ovos_workshop
    def show_notification(self, content, action=None, noticetype="transient"):
        """Display a Notification on homepage in the GUI.
        Arguments:
            content (str): Main text content of a notification, Limited
                          to two visual lines.
            action (str): Callback to any event registered by the skill
                         to perform a certain action when notification is
                         clicked.
            noticetype (str):
                transient: 'Default' displays a notification with a timeout.
                sticky: displays a notification that sticks to the screen.
        """
        self.bus.emit(Message("homescreen.notification.set",
                              data={
                                  "sender": self.skill_id,
                                  "text": content,
                                  "action": action,
                                  "type": noticetype
                              }))

    def handle_speak(self, message):
        if self.sleeping:
            utt = message.data["utterance"]
            self.show_notification(utt)

    @intent_handler(IntentBuilder("NapTimeIntent").require("SleepCommand"))
    def handle_go_to_sleep(self, message):
        """Sends a message to the speech client putting the listener to sleep.

        If the user has been told about the waking up process five times
        already, it sends a shorter message.
        """
        if self.wake_word:
            self.speak_dialog('going.to.sleep', {'wake_word': self.wake_word}, wait=True)
        else:
            self.speak_dialog('going.to.sleep.short', wait=True)

        self.bus.emit(Message('recognizer_loop:sleep'))
        self.sleeping = True
        self.started_by_skill = True
        self.bus.emit(Message('mycroft.volume.mute',
                              data={"speak_message": False}))
        if self.config_core['confirm_listening']:
            self.disable_confirm_listening()

    def handle_awoken(self, message):
        """Handler for the mycroft.awoken message

        The message is sent when the listener hears 'Hey Mycroft, Wake Up',
        this handles the user interaction upon wake up.
        """
        started_by_skill = self.started_by_skill
        self.awaken()
        if started_by_skill:
            # Announce that the unit is awake
            self.speak_dialog("i.am.awake", wait=True)

    def awaken(self):
        self.bus.emit(Message('mycroft.volume.unmute',
                              data={"speak_message": False}))
        if self.disabled_confirm_listening:
            self.enable_confirm_listening()
        self.sleeping = False
        self.started_by_skill = False

    def disable_confirm_listening(self):
        msg = Message('configuration.patch',
                      data={'config': {'confirm_listening': False}}
                      )
        self.bus.emit(msg)
        self.disabled_confirm_listening = True
        self.log.info('Disabled listen sound')

    def enable_confirm_listening(self):
        msg = Message('configuration.patch',
                      data={'config': {'confirm_listening': True}}
                      )
        self.bus.emit(msg)
        self.disabled_confirm_listening = False
        self.log.info('Enabled listen sound')


def create_skill():
    return NapTimeSkill()
