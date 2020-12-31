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
		self.airplay_enabled = False
		self.sshd_enabled = True
		self.spotify_enabled = False
		self.btspeaker_enabled = False
		self.snapclient_enabled = False
		self.airplay_enabled = self.settings.get('airplay')
		self.sshd_enabled = self.settings.get('sshd')
		self.spotify_enabled = self.settings.get('spotifyd')
		self.btspeaker_enabled = self.settings.get('btspeaker')
		self.snapclient_enabled = self.settings.get('snapclient')

	def initialize(self):
		""" Perform initalization.
		Registers messagebus handlers.
		"""
		
		# Handle settings change
		self.settings_change_callback = self.on_websettings_changed
			
		try:
			# Handle Device Ready
			self.bus.on('mycroft.ready', self.reset_screen)

			# Handle volume setting via PulseAudio
			#self.add_event('mycroft.volume.set', self.on_volume_set)
			#self.add_event('mycroft.volume.get', self.on_volume_get)
			#self.add_event('mycroft.volume.duck', self.on_volume_duck)
			#self.add_event('mycroft.volume.unduck', self.on_volume_unduck)

			# Administrative messages
			self.bus.on('system.shutdown', self.on_shutdown)
			self.bus.on('system.reboot', self.on_reboot)

		except Exception:
			LOG.exception('In MycroftOS Enclosure Skill')

	def on_websettings_changed(self):
		if self.sshd_enabled != self.settings.get('sshd'):
			if self.settings.get('sshd') is True:
				self.enable_ssh()
			else:
				self.disable_ssh()

		if self.airplay_enabled != self.settings.get('airplay'):
			if self.settings.get('airplay') is True:
				self.enable_airplay()
			else:
				self.disable_airplay()
		
		if self.spotify_enabled != self.settings.get('spotifyd'):
			if self.settings.get('spotifyd') is True:
				self.enable_spotify()
			else:
				self.disable_spotify()
		
		if self.btspeaker_enabled != self.settings.get('btspeaker'):
			if self.settings.get('btspeaker') is True:
				self.enable_btspeaker()
			else:
				self.disable_btspeaker()
		
		if self.snapclient_enabled != self.settings.get('snapclient'):
			if self.settings.get('snapclient') is True:
				self.enable_snapclient()
			else:
				self.disable_snapclient()

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

	# Device is fully started
	def reset_screen(self, message):
		"""Triggered after skills are initialized."""
		self.loading = False
		if is_paired():
			self.speak_dialog('finished.booting')


	# System actions
	def on_shutdown(self):
		self.speak('Till next time')
		sleep(5)
		os.system('sudo halt')

	def on_reboot(self):
		self.speak('I will be right back')
		sleep(5)
		os.system('sudo reboot')

	# System services
	def enable_ssh(self):
		self.settings['sshd'] = True
		if not os.path.isfile('/etc/systemd/system/multi-user.target.wants/sshd.service'):
			# Service not yet enabled
			os.system('sudo systemctl enable sshd.service')
			self.speak_dialog('EnabledSSH')
			if os.system('sudo systemctl is-active --quiet sshd.service') != 0:
				# Service not currently running
				os.system('sudo systemctl start sshd.service')

	def disable_ssh(self):
		self.settings['sshd'] = False
		if os.path.isfile('/etc/systemd/system/multi-user.target.wants/sshd.service'):
			# Service is enabled
			os.system('sudo systemctl disable sshd.service')
			self.speak_dialog('DisabledSSH')
		os.system('sudo systemctl stop sshd.service')
		
		self.sshd_enabled = False
		self.sshd_started = True
		

	def enable_airplay(self):
		os.system('sudo systemctl enable shairport-sync.service')
		os.system('sudo systemctl start shairport-sync.service')
		self.settings['airplay'] = True
		self.airplay_enabled = True
		self.airplay_started = True
		self.speak_dialog('EnabledAirPlay')

	def disable_airplay(self):
		os.system('sudo systemctl disable shairport-sync.service')
		os.system('sudo systemctl stop shairport-sync.service')
		self.settings['airplay'] = False
		self.airplay_enabled = False
		self.airplay_started = False
		self.speak_dialog('DisabledAirPlay')

	def enable_spotify(self):
		os.system('sudo systemctl enable spotifyd.service')
		os.system('sudo systemctl start spotifyd.service')
		self.settings['spotifyd'] = True
		self.spotify_enabled = True
		self.spotify_started = True
		self.speak_dialog('EnabledSpotify')

	def disable_spotify(self):
		os.system('sudo systemctl disable spotifyd.service')
		os.system('sudo systemctl stop spotifyd.service')
		self.settings['spotifyd'] = False
		self.spotify_enabled = False
		self.spotify_started = False
		self.speak_dialog('DisabledSpotify')

	def enable_btspeaker(self):
		os.system('sudo systemctl enable btspeaker.service')
		os.system('sudo systemctl start btspeaker.service')
		self.settings['btspeaker'] = True
		self.btspeaker_enabled = True
		self.btspeaker_started = True
		self.speak_dialog('EnabledBTspeaker')

	def disable_btspeaker(self):
		os.system('sudo systemctl disable btspeaker.service')
		os.system('sudo systemctl stop btspeaker.service')
		self.settings['btspeaker'] = False
		self.btspeaker_enabled = False
		self.btspeaker_started = False
		self.speak_dialog('DisabledBTspeaker')

	def enable_snapclient(self):
		os.system('sudo systemctl enable snapclient.service')
		os.system('sudo systemctl start snapclient.service')
		self.settings['snapclient'] = True
		self.snapclient_enabled = True
		self.snapclient_started = True
		self.speak_dialog('EnabledSnapclient')

	def disable_snapclient(self):
		os.system('sudo systemctl disable snapclient.service')
		os.system('sudo systemctl stop snapclient.service')
		self.settings['snapclient'] = False
		self.snapclient_enabled = False
		self.snapclient_started = False
		self.speak_dialog('DisabledSnapclient')


def create_skill():
	return MycroftOS()