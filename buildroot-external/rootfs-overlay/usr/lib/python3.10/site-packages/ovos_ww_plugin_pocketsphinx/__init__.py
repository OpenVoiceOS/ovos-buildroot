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
#
import os
import tempfile
from os.path import join, dirname

import speech_recognition as sr
from ovos_plugin_manager.templates.hotwords import HotWordEngine, msec_to_sec
from pocketsphinx import Decoder
from phoneme_guesser import get_phonemes


class PocketsphinxHotWordPlugin(HotWordEngine):
    """Wake word engine using PocketSphinx.

    PocketSphinx is very general purpose but has a somewhat high error rate.
    The key advantage is to be able to specify the wake word with phonemes.
    """

    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super().__init__(key_phrase, config, lang)

        # set default values if missing from config
        self.phonemes = self.config.get("phonemes") or \
                        self.get_phonemes(key_phrase, lang)
        num_phonemes = len(self.phonemes.split(" "))
        phoneme_duration = msec_to_sec(
            self.config.get('phoneme_duration', 120))
        self.expected_duration = self.config.get("expected_duration") or \
                                 num_phonemes * phoneme_duration
        self.hmm = self.config.get("hmm")
        if not self.hmm and self.lang.startswith("en"):
            self.hmm = self.get_default_english_model()
        elif not self.hmm:
            raise ValueError("No pocketsphinx hmm model provided")
        # read user params
        # TODO threshold is a bitch to automate, maybe raise exception ?
        self.threshold = self.config.get("threshold", 1e-30)

        self.sample_rate = self.config.get("sample_rate") or \
                           self.listener_config.get("sample_rate") or 16000
        dict_name = self.create_dict(self.key_phrase, self.phonemes)
        config = self.create_config(dict_name, Decoder.default_config())
        self.decoder = Decoder(config)

    @staticmethod
    def get_phonemes(key_phrase, lang="en-us"):
        return get_phonemes(key_phrase, lang).split(" ")

    @staticmethod
    def create_dict(key_phrase, phonemes):
        (fd, file_name) = tempfile.mkstemp()
        words = key_phrase.split()
        phoneme_groups = phonemes.split('.')
        with os.fdopen(fd, 'w') as f:
            for word, phoneme in zip(words, phoneme_groups):
                f.write(word + ' ' + phoneme + '\n')
        return file_name

    def create_config(self, dict_name, config):
        """If language config doesn't exist then
        we use default language (english) config as a fallback.
        """
        config.set_string('-hmm', self.hmm)
        config.set_string('-dict', dict_name)
        config.set_string('-keyphrase', self.key_phrase)
        config.set_float('-kws_threshold', float(self.threshold))
        config.set_float('-samprate', self.sample_rate)
        config.set_int('-nfft', 2048)
        logfn = '/dev/null'
        if os.name == 'nt': logfn = 'NUL'
        config.set_string('-logfn', logfn)
        return config

    @staticmethod
    def get_default_english_model():
        language_directory = join(dirname(sr.__file__),
                                  "pocketsphinx-data", "en-US")
        return join(language_directory, "acoustic-model")

    def found_wake_word(self, frame_data):
        self.decoder.start_utt()
        self.decoder.process_raw(frame_data, False, False)
        self.decoder.end_utt()
        hyp = self.decoder.hyp()
        return hyp and self.key_phrase in hyp.hypstr.lower()
