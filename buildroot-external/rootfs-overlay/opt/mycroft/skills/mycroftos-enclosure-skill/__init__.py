# Copyright 2019 j1nx - http://www.j1nx.nl.
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

import subprocess
import os
import sys

from mycroft.api import is_paired
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import LOG
from mycroft.util.parse import normalize
from mycroft.util import play_wav
from mycroft import intent_file_handler

class MycroftOS(MycroftSkill):
	"""
	The MycroftOS skill handles much of the screen and audio activities
	related to Mycroft's core functionality.
	"""
	def __init__(self):
		super().__init__('MycroftOS')
		self.skip_list = ('MycroftOS')
		self.loading = True
		self.airplay = self.settings.get('airplay')
		self.sshd = self.settings.get('sshd')
		self.spotify = self.settings.get('spotifyd')
		self.btspeaker = self.settings.get('btspeaker')
		self.snapclient = self.settings.get('snapclient')
		self.snapserver = self.settings.get('snapserver')
		self.mpd = self.settings.get('mpd')

	def initialize(self):
		""" Perform initalization.
		Registers messagebus handlers.
		"""
		
		# Handle settings change
		self.settings_change_callback = self.on_websettings_changed
			
		try:
		
			# Handle the 'waking' visual
			self.add_event('recognizer_loop:wakeword',
					self.handle_listener_started)
			self.add_event('recognizer_loop:record_end',
					self.handle_listener_ended)
			self.add_event('mycroft.speech.recognition.unknown',
					self.handle_failed_stt)

			# Handle Device Ready
			self.bus.on('mycroft.ready', self.reset_screen)

			# Handle the 'busy' visual
			self.bus.on('mycroft.skill.handler.start',
					self.on_handler_started)
			self.bus.on('mycroft.skill.handler.complete',
					self.on_handler_complete)

			# Handle the 'speaking' visual
			self.bus.on('recognizer_loop:audio_output_start',
					self.on_handler_audio_start)
			self.bus.on('recognizer_loop:audio_output_end',
					self.on_handler_audio_end)

			# Handle volume setting via PulseAudio
			#self.add_event('mycroft.volume.set', self.on_volume_set)
			#self.add_event('mycroft.volume.get', self.on_volume_get)
			#self.add_event('mycroft.volume.duck', self.on_volume_duck)
			#self.add_event('mycroft.volume.unduck', self.on_volume_unduck)

			# Administrative messages
			self.bus.on('system.shutdown', self.on_shutdown)
			self.bus.on('system.reboot', self.on_reboot)

		except Exception:
			LOG.exception('In MycroftOS Skill')

	def on_websettings_changed(self):
		if self.sshd != self.settings.get('sshd'):
			if self.settings.get('sshd') is True:
				self.enable_ssh()
			else:
				self.disable_ssh()

		if self.airplay != self.settings.get('airplay'):
			if self.settings.get('airplay') is True:
				self.enable_airplay()
			else:
				self.disable_airplay()
		
		if self.spotify != self.settings.get('spotifyd'):
			if self.settings.get('spotifyd') is True:
				self.enable_spotify()
			else:
				self.disable_spotify()
		
		if self.btspeaker != self.settings.get('btspeaker'):
			if self.settings.get('btspeaker') is True:
				self.enable_btspeaker()
			else:
				self.disable_btspeaker()
		
		if self.snapclient != self.settings.get('snapclient'):
			if self.settings.get('snapclient') is True:
				self.enable_snapclient()
			else:
				self.disable_snapclient()
		
		if self.snapserver != self.settings.get('snapserver'):
			if self.settings.get('snapserver') is True:
				self.enable_snapserver()
			else:
				self.disable_snapserver()
		
		if self.mpd != self.settings.get('mpd'):
			if self.settings.get('mpd') is True:
				self.enable_mpd()
			else:
				self.disable_mpd()

	# System volume
	#def on_volume_set(self, message):
	#	self.muted = False
	#	self.set_pulse_volume(vol)

	#def on_volume_get(self, message):
	#	self.bus.emit(message.response(data={'percent': self.volume, 'muted': self.muted}))

	#def on_volume_duck(self, message):
	#	self.muted = True
        #        call(['pactl', 'set-sink-mute', '0', '1'])

	#def on_volume_unduck(self, message):
	#	self.muted = False
	#	call(['pactl', 'set-sink-mute', '0', '0'])

	# Cleanup
	def shutdown(self):
		# Gotta clean up manually since not using add_event()
		self.bus.remove('mycroft.skill.handler.start',
				self.on_handler_started)
		self.bus.remove('mycroft.skill.handler.complete',
				self.on_handler_complete)
		self.bus.remove('recognizer_loop:audio_output_start',
				self.on_handler_audio_start)
		self.bus.remove('recognizer_loop:audio_output_end',
				self.on_handler_audio_end)

	# Handlers
	def on_handler_audio_start(self, message):
		self.speaking = True
		#framebuffer speaking visual
		os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/speaking.png > /dev/null 2>&1')

	def on_handler_audio_end(self, message):
		self.speaking = False
		#framebuffer background
		os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/background.png > /dev/null 2>&1')

	def on_handler_started(self, message):
		handler = message.data.get('handler', '')
		if self._skip_handler(handler):
			return
		#framebuffer thinking visual
		os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/thinking.png > /dev/null 2>&1')

	def on_handler_complete(self, message):
		handler = message.data.get('handler', '')
		if self._skip_handler(handler):
			return

		# If speaking has already begun, on_handler_audio_end will
		# turn off the framebuffer
		if not self.speaking:
			#framebuffer background
			os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/background.png > /dev/null 2>&1')

	def _skip_handler(self, handler):
		#Ignoring handlers from this skill
		return any(skip in handler for skip in self.skip_list)

	def handle_listener_started(self, message):
		#framebuffer listen visual
		os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/listen.png > /dev/null 2>&1')

	def handle_listener_ended(self, message):
		#framebuffer background
		os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/background.png > /dev/null 2>&1')

	def handle_failed_stt(self, message):
		#framebuffer background
		os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/background.png > /dev/null 2>&1')


	# Device is fully started
	def reset_screen(self, message):
		"""Triggered after skills are initialized."""
		self.loading = False
		if is_paired():
			os.system('fbv -f -d 1 /opt/mycroft/skills/mycroftos-enclosure-skill/ui/background.png > /dev/null 2>&1')
			self.speak_dialog('finished.booting')


	# System actions
	def on_shutdown(self, message):
		self.speak('Till next time')
		sleep(5)
		os.system('sudo halt')

	def on_reboot(self, message):
		self.speak('I will be right back')
		sleep(5)
		os.system('sudo reboot')

	def enable_ssh(self):
		os.system('sudo systemctl enable sshd.service')
		os.system('sudo systemctl start sshd.service')
		self.settings['sshd'] = True
		self.sshd = True
		self.speak_dialog('EnabledSSH')
	
	def disable_ssh(self):
		os.system('sudo systemctl disable sshd.service')
		os.system('sudo systemctl stop sshd.service')
		self.settings['sshd'] = False
		self.sshd = False
		self.speak_dialog('DisabledSSH')
		
	def enable_airplay(self):
		os.system('sudo systemctl enable shairport-sync.service')
		os.system('sudo systemctl start shairport-sync.service')
		self.settings['airplay'] = True
		self.airplay = True
		self.speak_dialog('EnabledAirPlay')
		
	def disable_airplay(self):
		os.system('sudo systemctl disable shairport-sync.service')
		os.system('sudo systemctl stop shairport-sync.service')
		self.settings['airplay'] = False
		self.airplay = False
		self.speak_dialog('DisabledAirPlay')
	
	def enable_spotify(self):
		os.system('sudo systemctl enable spotifyd.service')
		os.system('sudo systemctl start spotifyd.service')
		self.settings['spotifyd'] = True
		self.spotify = True
		self.speak_dialog('EnabledSpotify')
		
	def disable_spotify(self):
		os.system('sudo systemctl disable spotifyd.service')
		os.system('sudo systemctl stop spotifyd.service')
		self.settings['spotifyd'] = False
		self.spotify = False
		self.speak_dialog('DisabledSpotify')
	
	def enable_btspeaker(self):
		os.system('sudo systemctl enable btspeaker.service')
		os.system('sudo systemctl start btspeaker.service')
		self.settings['btspeaker'] = True
		self.btspeaker = True
		self.speak_dialog('EnabledBTspeaker')
		
	def disable_btspeaker(self):
		os.system('sudo systemctl disable btspeaker.service')
		os.system('sudo systemctl stop btspeaker.service')
		self.settings['btspeaker'] = False
		self.btspeaker = False
		self.speak_dialog('DisabledBTspeaker')
	
	def enable_snapclient(self):
		os.system('sudo systemctl enable snapclient.service')
		os.system('sudo systemctl start snapclient.service')
		self.settings['snapclient'] = True
		self.snapclient = True
		self.speak_dialog('EnabledSnapclient')
		
	def disable_snapclient(self):
		os.system('sudo systemctl disable snapclient.service')
		os.system('sudo systemctl stop snapclient.service')
		self.settings['snapclient'] = False
		self.snapclient = False
		self.speak_dialog('DisabledSnapclient')
	
	def enable_snapserver(self):
		os.system('sudo systemctl enable snapserver.service')
		os.system('sudo systemctl start snapserver.service')
		self.settings['snapserver'] = True
		self.snapserver = True
		self.speak_dialog('EnabledSnapserver')
		
	def disable_snapserver(self):
		os.system('sudo systemctl disable snapserver.service')
		os.system('sudo systemctl stop snapserver.service')
		self.settings['snapserver'] = False
		self.snapserver = False
		self.speak_dialog('DisabledSnapserver')
	
	def enable_mpd(self):
		os.system('sudo systemctl enable mpd.service')
		os.system('sudo systemctl start mpd.service')
		self.settings['mpd'] = True
		self.mpd = True
		self.speak_dialog('EnabledMPD')
		
	def disable_mpd(self):
		os.system('sudo systemctl disable mpd.service')
		os.system('sudo systemctl stop mpd.service')
		self.settings['mpd'] = False
		self.mpd = False
		self.speak_dialog('DisabledMPD')


	# Intent handlers
	@intent_file_handler('EnableSSH.intent')
	def on_enable_ssh(self, message):
		if self.sshd is False:
			self.enable_ssh()
		else:
			self.speak_dialog('AlreadyEnabledSSH')

	@intent_file_handler('DisableSSH.intent')
	def on_disable_ssh(self, message):
		if self.sshd is True:
			self.disable_ssh()
		else:
			self.speak_dialog('AlreadyDisabledSSH')

	@intent_file_handler('EnableAirPlay.intent')
	def on_enable_airplay(self, message):
		if self.airplay is False:
			self.enable_airplay()
		else:
			self.speak_dialog('AlreadyEnabledAirPlay')

	@intent_file_handler('DisableAirPlay.intent')
	def on_disable_airplay(self, message):
		if self.airplay is True:
			self.disable_airplay()
		else:
			self.speak_dialog('AlreadyDisabledAirPlay')

	@intent_file_handler('EnableSpotify.intent')
	def on_enable_spotify(self, message):
		if self.spotify is False:
			self.enable_spotify()
		else:
			self.speak_dialog('AlreadyEnabledSpotify')

	@intent_file_handler('DisableSpotify.intent')
	def on_disable_spotify(self, message):
		if self.spotify is True:
			self.disable_spotify()
		else:
			self.speak_dialog('AlreadyDisabledSpotify')
	
	@intent_file_handler('EnableBTspeaker.intent')
	def on_enable_btspeaker(self, message):
		if self.btspeaker is False:
			self.enable_btspeaker()
		else:
			self.speak_dialog('AlreadyEnabledBTspeaker')

	@intent_file_handler('DisableBTspeaker.intent')
	def on_disable_btspeaker(self, message):
		if self.btspeaker is True:
			self.disable_btspeaker()
		else:
			self.speak_dialog('AlreadyDisabledBTspeaker')
	
	@intent_file_handler('EnableSnapclient.intent')
	def on_enable_snapclient(self, message):
		if self.snapclient is False:
			self.enable_snapclient()
		else:
			self.speak_dialog('AlreadyEnabledSnapclient')

	@intent_file_handler('DisableSnapclient.intent')
	def on_disable_snapclient(self, message):
		if self.snapclient is True:
			self.disable_snapclient()
		else:
			self.speak_dialog('AlreadyDisabledSnapclient')
	
	@intent_file_handler('EnableSnapserver.intent')
	def on_enable_snapserver(self, message):
		if self.snapserver is False:
			self.enable_snapserver()
		else:
			self.speak_dialog('AlreadyEnabledSnapserver')

	@intent_file_handler('DisableSnapserver.intent')
	def on_disable_snapserver(self, message):
		if self.snapserver is True:
			self.disable_snapserver()
		else:
			self.speak_dialog('AlreadyDisabledSnapserver')
	
	@intent_file_handler('EnableMPD.intent')
	def on_enable_mpd(self, message):
		if self.mpd is False:
			self.enable_mpd()
		else:
			self.speak_dialog('AlreadyEnabledMPD')

	@intent_file_handler('DisableMPD.intent')
	def on_disable_mpd(self, message):
		if self.mpd is True:
			self.disable_mpd()
		else:
			self.speak_dialog('AlreadyDisabledMPD')


def create_skill():
	return MycroftOS()