# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
#    and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
#    and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from speech_recognition import AudioData
from ovos_plugin_manager.audio_transformers import find_audio_transformer_plugins, load_audio_transformer_plugin
from ovos_plugin_manager.utils import load_plugin, find_plugins, PluginTypes
from neon_transformers.streams import ReadWriteStream
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.json_helper import merge_dict
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
from neon_transformers.tasks import AudioTask


class AudioTransformer:
    """process audio data and optionally transform it before STT stage"""
    task = AudioTask.OTHER

    def __init__(self, name, priority=50, config=None):
        self.name = name
        self.bus = None
        self.priority = priority
        self.config = config or self._read_mycroft_conf()

        # listener config
        self.sample_width = self.config.get("sample_width", 2)
        self.channels = self.config.get("channels", 1)
        self.sample_rate = self.config.get("sample_rate", 16000)

        # buffers with audio chunks to be used in predictions
        # always cleared before STT stage
        self.noise_feed = ReadWriteStream()
        self.hotword_feed = ReadWriteStream()
        self.speech_feed = ReadWriteStream()

    def _read_mycroft_conf(self):
        config_core = read_mycroft_config()
        config = config_core.get("audio_transformers", {}).get(self.name) or {}
        listener_config = config_core.get("listener") or {}
        for k in ["sample_width", "sample_rate", "channels"]:
            if k not in config and k in listener_config:
                config[k] = listener_config[k]
        return config

    def bind(self, bus=None):
        """ attach messagebus """
        self.bus = bus or get_mycroft_bus()

    def feed_audio_chunk(self, chunk):
        chunk = self.on_audio(chunk)
        self.noise_feed.write(chunk)

    def feed_hotword_chunk(self, chunk):
        chunk = self.on_hotword(chunk)
        self.hotword_feed.write(chunk)

    def feed_speech_chunk(self, chunk):
        chunk = self.on_audio(chunk)
        self.speech_feed.write(chunk)

    def feed_speech_utterance(self, chunk):
        return self.on_speech_end(chunk)

    def reset(self):
        # end of prediction, reset buffers
        self.speech_feed.clear()
        self.hotword_feed.clear()
        self.noise_feed.clear()

    def initialize(self):
        """ perform any initialization actions """
        pass

    def on_audio(self, audio_data):
        """ Take any action you want, audio_data is a non-speech chunk
        """
        return audio_data

    def on_hotword(self, audio_data):
        """ Take any action you want, audio_data is a full wake/hotword
        Common action would be to prepare to received speech chunks
        NOTE: this might be a hotword or a wakeword, listening is not assured
        """
        return audio_data

    def on_speech(self, audio_data):
        """ Take any action you want, audio_data is a speech chunk (NOT a
        full utterance) during recording
        """
        return audio_data

    def on_speech_end(self, audio_data):
        """ Take any action you want, audio_data is the full speech audio
        """
        return audio_data

    def transform(self, audio_data):
        """ return any additional message context to be passed in
        recognize_loop:utterance message, usually a streaming prediction
        Optionally make the prediction here with saved chunks from other handlers
        """
        return audio_data, {}

    def default_shutdown(self):
        """ perform any shutdown actions """
        pass


class AudioTransformersService:

    def __init__(self, bus, config=None):
        self.config_core = config or {}
        self.loaded_modules = {}
        self.has_loaded = False
        self.bus = bus
        self.config = self.config_core.get("audio_transformers") or {"neon_noise_level_plugin": {}}
        self.load_plugins()

    def load_plugins(self):
        for plug_name, plug in find_audio_transformer_plugins().items():
            if plug_name in self.config:
                # if disabled skip it
                if not self.config[plug_name].get("active", True):
                    continue
                try:
                    self.loaded_modules[plug_name] = plug()
                    LOG.info(f"loaded audio transfomer plugin: {plug_name}")
                except Exception as e:
                    LOG.exception(f"Failed to load audio transfomer plugin: {plug_name}")

    @property
    def modules(self):
        return sorted(self.loaded_modules.values(),
                      key=lambda k: k.priority, reverse=True)

    def shutdown(self):
        for module in self.modules:
            try:
                module.shutdown()
            except:
                pass

    def get_chunk(self, audio_data):
        if isinstance(audio_data, AudioData):
            chunk = audio_data.frame_data
            for module in self.modules:
                module.sample_rate = audio_data.sample_rate
                module.sample_width = audio_data.sample_width
        else:
            chunk = audio_data
        return chunk

    def feed_audio(self, audio_data):
        chunk = self.get_chunk(audio_data)
        for module in self.modules:
            module.feed_audio_chunk(chunk)

    def feed_hotword(self, audio_data):
        chunk = self.get_chunk(audio_data)
        for module in self.modules:
            module.feed_hotword_chunk(chunk)

    def feed_speech(self, audio_data):
        chunk = self.get_chunk(audio_data)
        for module in self.modules:
            module.feed_speech_chunk(chunk)

    def transform(self, audio_data):
        context = {}
        chunk = self.get_chunk(audio_data)
        for module in self.modules:
            try:
                chunk = module.feed_speech_utterance(chunk)
                chunk, data = module.transform(chunk)
                LOG.debug(f"{module.name}: {data}")
                context = merge_dict(context, data)
            except:
                pass
        # core expects a AudioData object
        audio_data.frame_data = chunk
        return audio_data, context
