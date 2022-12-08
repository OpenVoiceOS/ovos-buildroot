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
import subprocess
from distutils.spawn import find_executable
from os.path import join, isfile, expanduser

from ovos_plugin_manager.templates.tts import TTS, TTSValidator
from ovos_utils.configuration import get_xdg_base
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.lang.visimes import VISIMES
from ovos_utils.xdg_utils import xdg_config_home


class MimicTTSPlugin(TTS):
    """Interface to Mimic TTS."""

    def __init__(self, lang="en-us", config=None):
        super(MimicTTSPlugin, self).__init__(lang, config,
                                             MimicTTSValidator(self), 'wav')
        self.mimic_bin = self.config.get("binary") or \
                         self.find_premium_mimic() or \
                         find_executable("mimic")
        self.voice = self.voice or "ap"

    @staticmethod
    def find_premium_mimic():
        # HolmesV style
        xdg_mimic = join(xdg_config_home(), get_xdg_base(),
                         'voices', 'mimic_tn')
        if isfile(xdg_mimic):
            return xdg_mimic

        # HolmesV style default / once mycroft finally migrates to xdg
        xdg_mimic = join(xdg_config_home(), "mycroft",
                         'voices', 'mimic_tn')
        if isfile(xdg_mimic):
            return xdg_mimic

        # mycroft style data_dir
        try:
            config = read_mycroft_config() or {}
            if config.get("data_dir"):
                data_dir = expanduser(config['data_dir'])
                mimic_bin = join(data_dir, 'voices', 'mimic_tn')
                if isfile(mimic_bin):
                    return mimic_bin
        except:  # not running mycroft-core -> no default config
            pass

        # mycroft default location
        mimic_bin = "/opt/mycroft/voices/mimic_tn"
        if isfile(mimic_bin):
            return mimic_bin

    @staticmethod
    def modify_tag(tag):
        """Modify the SSML to suite Mimic."""
        ssml_conversions = {
            'x-slow': '0.4',
            'slow': '0.7',
            'medium': '1.0',
            'high': '1.3',
            'x-high': '1.6',
            'speed': 'rate'
        }
        for key, value in ssml_conversions.items():
            tag = tag.replace(key, value)
        return tag

    @staticmethod
    def parse_phonemes(phonemes):
        """Parse mimic phoneme string into a list of phone, duration pairs.

        Arguments
            phonemes (bytes): phoneme output from mimic
        Returns:
            (list) list of phoneme duration pairs
        """
        phon_str = phonemes.decode()
        pairs = phon_str.split(' ')
        return [pair.split(':') for pair in pairs if ':' in pair]

    def get_builtin_voices(self):
        return subprocess.check_output(
            [expanduser(self.mimic_bin), '-lv']). \
            decode("utf-8").split(":")[-1].strip().split(" ")

    def get_tts(self, sentence, wav_file, lang=None, voice=None):
        """Generate WAV and phonemes.

        Arguments:
            sentence (str): sentence to generate audio for
            wav_file (str): output file
            lang (str): optional lang override
            voice (str): optional voice override

        Returns:
            tuple ((str) file location, (str) generated phonemes)
        """
        voice = voice or self.voice or "ap"
        args = [expanduser(self.mimic_bin), '-voice', voice,
                '-psdur', '-ssml']

        stretch = self.config.get('duration_stretch', None)
        if stretch:
            args += ['--setf', f'duration_stretch={stretch}']
        phonemes = subprocess.check_output(args + ['-o', wav_file,
                                                   '-t', sentence])

        return wav_file, self.parse_phonemes(phonemes)

    def viseme(self, phoneme_pairs):
        """Convert phoneme string to visemes.

        Arguments:
            phoneme_pairs (list): Phoneme output from mimic

        Returns:
            (list) list of tuples of viseme and duration
        """
        visemes = []
        for phon, dur in phoneme_pairs:
            visemes.append((VISIMES.get(phon, '4'), float(dur)))
        return visemes

    @property
    def available_languages(self) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set(MimicTTSPluginConfig.keys())


class MimicTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(MimicTTSValidator, self).__init__(tts)

    def validate_voice(self):
        if self.tts.voice is not None and \
                not self.tts.voice.startswith("http") and \
                not self.tts.voice.startswith("/"):
            assert self.tts.voice in self.tts.get_builtin_voices()

    def validate_connection(self):
        pass

    def get_tts_class(self):
        return MimicTTSPlugin


MimicTTSPluginConfig = {
    "en-gb": [
        {"voice": "ap", "meta": {"gender": "male", "display_name": "Alan Pope", "offline": True, "priority": 50}}
    ],
    "en-us": [
        {"voice": "slt", "meta": {"gender": "female", "display_name": "slt", "offline": True, "priority": 70}},
        {"voice": "kal", "meta": {"gender": "male", "display_name": "kal", "offline": True, "priority": 70}},
        {"voice": "awb", "meta": {"gender": "male", "display_name": "awb", "offline": True, "priority": 70}},
        {"voice": "rms", "meta": {"gender": "male", "display_name": "rms", "offline": True, "priority": 70}}
    ]
}

if MimicTTSPlugin.find_premium_mimic():
    MimicTTSPluginConfig["en-us"].append(
        {"voice": "trinity", "meta": {"gender": "female", "display_name": "Trinity", "offline": True, "priority": 50}}
    )
