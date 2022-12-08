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
import re

import requests
from ovos_plugin_manager.templates.tts import TTS, RemoteTTSException
from ovos_utils.log import LOG


class Mimic3ServerTTSPlugin(TTS):
    """Interface to Mimic3 Server TTS."""
    public_servers = [
        "http://mycroft.blue-systems.com:59125/api/tts",
        "https://mimic3.ziggyai.online",
        "https://mimic3.jarbasai.online"
    ]
    default_voices = {
        # TODO add default voice for every lang
        "en": "en_US/cmu-arctic_low",
        "en-uk": "en_UK/apope_low",
        "en-gb": "en_UK/apope_low",
        "de": "de_DE/thorsten_low",
        "bn": "bn/multi_low",
        "af": "af_ZA/google-nwu_low",
        "es": "es_ES/m-ailabs_low",
        "fa": "fa/haaniye_low",
        "fi": "fi_FI/harri-tapani-ylilammi_low",
        "fr": "fr_FR/m-ailabs_low",
        "it": "it_IT/mls_low",
        "ko": "ko_KO/kss_low",
        "nl": "nl/bart-de-leeuw_low",
        "pl": "pl_PL/m-ailabs_low",
        "ru": "ru_RU/multi_low",
        "uk": "uk_UK/m-ailabs_low"
    }

    def __init__(self, lang="en-us", config=None):
        ssml_tags = ["speak", "s", "w", "voice", "prosody", "say-as", "break", "sub", "phoneme"]
        config = config or {}
        if "voice" not in config:
            if lang not in self.default_voices:
                lang = lang.split("-")[0]
            if lang in self.default_voices:
                voice = self.default_voices[lang]
                config["voice"] = voice
            else:
                LOG.warning("Default mimic3 voice not set!")
        super().__init__(lang, config, audio_ext='wav', ssml_tags=ssml_tags)
        self.url = self.config.get("url")

    def _validate_args_combo(self, lang=None, voice=None, speaker=None):
        if voice:
            if "#" in voice:
                voice, new_speaker = voice.split("#")
                if speaker and speaker != new_speaker:
                    LOG.warning(f"speaker defined twice! choosing {new_speaker} over {speaker} for voice: {voice}")
                speaker = new_speaker
        elif lang:
            if lang not in self.default_voices:
                lang = lang.split("-")[0]
            if lang in self.default_voices:
                voice = self.default_voices[lang]
            else:
                raise ValueError(f"Selected lang {lang} is not supported!")
        elif speaker:
            pass  # TODO validate speaker is valid for default voice
        else:
            LOG.debug("using mimic3 default config, no voice requested")
            return self.voice

        if speaker and not voice.endswith(f"#{speaker}"):
            voice = f"{voice}#{speaker}"

        if lang:
            a, b = lang.split("-")
            lang = f"{a}_{b.upper()}"

            if "/" in voice:
                new_lang = voice.split("/")[0]
                if new_lang == "en_UK" and lang != "en_UK":
                    new_lang = "en_GB"  # mimic3 uses wrong lang code
                if new_lang != lang:
                    LOG.warning(f"lang defined twice! choosing {new_lang} over {lang} for voice: {voice}")
                    lang = new_lang
                voice = voice.split("/")[-1]

            if lang == "en_GB":
                lang = "en_UK"  # mimic3 uses wrong lang code
            if not voice.startswith(lang):
                voice = f"{lang}/{voice}"

        return voice

    def get_tts(self, sentence, wav_file, lang=None,
                voice=None, speaker=None):
        """Fetch tts audio using mimic3 endpoint.

        Arguments:
            sentence (str): Sentence to generate audio for
            wav_file (str): output file path
        Returns:
            Tuple ((str) written file, None)
        """
        voice = self._validate_args_combo(lang, voice, speaker)

        sentence, ssml = self._apply_text_hacks(sentence)

        if not self.url:
            # Try all public urls until one works
            audio_data = self._get_from_public_servers(voice, sentence)
        else:
            r = requests.post(self.url, params={"voice": voice}, data=sentence)
            if not r.ok:
                raise RemoteTTSException(f"Mimic3 server error: {r.reason}")
            else:
                audio_data = r.content

        with open(wav_file, "wb") as f:
            f.write(audio_data)

        return (wav_file, None)

    def _get_from_public_servers(self, voice, sentence):
        for url in self.public_servers:
            try:
                r = requests.post(url, params={"voice": voice}, data=sentence)
                if r.ok:
                    return r.content
            except:
                continue
        raise RemoteTTSException(f"All Mimic3 public servers are down, please self host mimic3")

    @staticmethod
    def _apply_text_hacks(sentence: str):
        """Mycroft-specific workarounds for mimic3 text.

        Returns: (text, ssml)
        """

        # HACK: Mycroft gives "eight a.m.next sentence" sometimes
        sentence = sentence.replace(" a.m.", " a.m. ")
        sentence = sentence.replace(" p.m.", " p.m. ")

        # A I -> A.I.
        sentence = re.sub(
            r"\b([A-Z](?: |$)){2,}",
            lambda m: m.group(0).strip().replace(" ", ".") + ". ",
            sentence,
        )

        # Assume SSML if sentence begins with an angle bracket
        ssml = sentence.strip().startswith("<")

        # HACK: Speak single letters from Mycroft (e.g., "A;")
        if (len(sentence) == 2) and sentence.endswith(";"):
            letter = sentence[0]
            ssml = True
            sentence = f'<say-as interpret-as="spell-out">{letter}</say-as>'
        else:
            # HACK: 'A' -> spell out
            sentence, subs_made = re.subn(
                r"'([A-Z])'",
                r'<say-as interpret-as="spell-out">\1</say-as>',
                sentence,
            )
            if subs_made > 0:
                ssml = True

        return (sentence, ssml)

    @property
    def available_languages(self) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set(Mimic3ServerTTSPluginConfig.keys())


# TODO manually check gender of each voice and add below
Mimic3ServerTTSPluginConfig = {
    'af-za': [
        {'speaker': '7214', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 7214', 'gender': '', 'priority': 50}},
        {'speaker': '8963', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8963', 'gender': '', 'priority': 50}},
        {'speaker': '7130', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 7130', 'gender': '', 'priority': 50}},
        {'speaker': '8924', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8924', 'gender': '', 'priority': 50}},
        {'speaker': '8148', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8148', 'gender': '', 'priority': 50}},
        {'speaker': '1919', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 1919', 'gender': '', 'priority': 50}},
        {'speaker': '2418', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 2418', 'gender': '', 'priority': 50}},
        {'speaker': '6590', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 6590', 'gender': '', 'priority': 50}},
        {'speaker': '0184', 'voice': 'af_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 0184', 'gender': '', 'priority': 50}}],
    'bn': [
        {'speaker': 'rm', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - Rm', 'gender': '', 'priority': 50}},
        {'speaker': '03042', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 03042', 'gender': '', 'priority': 50}},
        {'speaker': '00737', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 00737', 'gender': '', 'priority': 50}},
        {'speaker': '01232', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 01232', 'gender': '', 'priority': 50}},
        {'speaker': '02194', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 02194', 'gender': '', 'priority': 50}},
        {'speaker': '3108', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 3108', 'gender': '', 'priority': 50}},
        {'speaker': '3713', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 3713', 'gender': '', 'priority': 50}},
        {'speaker': '1010', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 1010', 'gender': '', 'priority': 50}},
        {'speaker': '00779', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 00779', 'gender': '', 'priority': 50}},
        {'speaker': '9169', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 9169', 'gender': '', 'priority': 50}},
        {'speaker': '4046', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 4046', 'gender': '', 'priority': 50}},
        {'speaker': '5958', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 5958', 'gender': '', 'priority': 50}},
        {'speaker': '01701', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 01701', 'gender': '', 'priority': 50}},
        {'speaker': '4811', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 4811', 'gender': '', 'priority': 50}},
        {'speaker': '0834', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 0834', 'gender': '', 'priority': 50}},
        {'speaker': '3958', 'voice': 'bn/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - 3958', 'gender': '', 'priority': 50}}],
    'de-de': [
        {'speaker': 'default', 'voice': 'de_DE/thorsten_low',
         'meta': {'offline': False, 'display_name': 'Thorsten', 'gender': '', 'priority': 30}},
        {'speaker': 'amused', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Amused', 'gender': '', 'priority': 45}},
        {'speaker': 'angry', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Angry', 'gender': '', 'priority': 45}},
        {'speaker': 'disgusted', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Disgusted', 'gender': '', 'priority': 45}},
        {'speaker': 'drunk', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Drunk', 'gender': '', 'priority': 45}},
        {'speaker': 'neutral', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Neutral', 'gender': '', 'priority': 45}},
        {'speaker': 'sleepy', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Sleepy', 'gender': '', 'priority': 45}},
        {'speaker': 'surprised', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Surprised', 'gender': '', 'priority': 45}},
        {'speaker': 'whisper', 'voice': 'de_DE/thorsten-emotion_low',
         'meta': {'offline': False, 'display_name': 'Thorsten-Emotion - Whisper', 'gender': '', 'priority': 45}},
        {'speaker': 'ramona_deininger', 'voice': 'de_DE/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Ramona Deininger', 'gender': '', 'priority': 31}},
        {'speaker': 'karlsson', 'voice': 'de_DE/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Karlsson', 'priority': 31, 'gender': ''}},
        {'speaker': 'rebecca_braunert_plunkett', 'voice': 'de_DE/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Rebecca Braunert Plunkett', 'priority': 31,
                  'gender': ''}},
        {'speaker': 'eva_k', 'voice': 'de_DE/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Eva K', 'priority': 31, 'gender': ''}},
        {'speaker': 'angela_merkel', 'voice': 'de_DE/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Angela Merkel', 'priority': 31, 'gender': ''}}],
    'el-gr': [
        {'speaker': 'default', 'voice': 'el_GR/rapunzelina_low',
         'meta': {'offline': False, 'display_name': 'Rapunzelina', 'priority': 40, 'gender': ''}}],
    'en-gb': [
        {'speaker': 'default', 'voice': 'en_UK/apope_low',
         'meta': {'offline': False, 'display_name': 'Apope', 'priority': 30, 'gender': 'male'}}],
    'en-us': [
        {'speaker': 'slt', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Slt', 'gender': 'female', 'priority': 40}},
        {'speaker': 'awb', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Awb', 'gender': 'male', 'priority': 40}},
        {'speaker': 'rms', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Rms', 'gender': 'male', 'priority': 40}},
        {'speaker': 'ksp', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Ksp', 'gender': 'male', 'priority': 40}},
        {'speaker': 'clb', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Clb', 'gender': 'female', 'priority': 40}},
        {'speaker': 'aew', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Aew', 'gender': 'male', 'priority': 40}},
        {'speaker': 'bdl', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Bdl', 'gender': 'male', 'priority': 40}},
        {'speaker': 'lnh', 'voice': 'en_US/cmu-arctic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Arctic - Lnh', 'gender': 'female', 'priority': 40}},
        {'speaker': '9017', 'voice': 'en_US/hifi-tts_low',
         'meta': {'offline': False, 'display_name': 'Hifi-Tts - 9017', 'gender': 'male', 'priority': 40}},
        {'speaker': '6097', 'voice': 'en_US/hifi-tts_low',
         'meta': {'offline': False, 'display_name': 'Hifi-Tts - 6097', 'gender': 'male', 'priority': 40}},
        {'speaker': '92', 'voice': 'en_US/hifi-tts_low',
         'meta': {'offline': False, 'display_name': 'Hifi-Tts - 92', 'gender': 'female', 'priority': 40}},
        {'speaker': 'default', 'voice': 'en_US/ljspeech_low',
         'meta': {'offline': False, 'display_name': 'Ljspeech', 'gender': 'female', 'priority': 45}},
        {'speaker': 'elliot_miller', 'voice': 'en_US/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Elliot Miller', 'gender': 'male', 'priority': 40}},
        {'speaker': 'judy_bieber', 'voice': 'en_US/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Judy Bieber', 'gender': 'female', 'priority': 40}},
        {'speaker': 'mary_ann', 'voice': 'en_US/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Mary Ann', 'gender': 'female', 'priority': 45}},
        {'speaker': 'p239', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P239', 'gender': '', 'priority': 41}},
        {'speaker': 'p236', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P236', 'gender': '', 'priority': 41}},
        {'speaker': 'p264', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P264', 'gender': '', 'priority': 41}},
        {'speaker': 'p250', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P250', 'gender': '', 'priority': 41}},
        {'speaker': 'p259', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P259', 'gender': '', 'priority': 41}},
        {'speaker': 'p247', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P247', 'gender': '', 'priority': 41}},
        {'speaker': 'p261', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P261', 'gender': '', 'priority': 41}},
        {'speaker': 'p263', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P263', 'gender': '', 'priority': 41}},
        {'speaker': 'p283', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P283', 'gender': '', 'priority': 41}},
        {'speaker': 'p274', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P274', 'gender': '', 'priority': 41}},
        {'speaker': 'p286', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P286', 'gender': '', 'priority': 41}},
        {'speaker': 'p276', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P276', 'gender': '', 'priority': 41}},
        {'speaker': 'p270', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P270', 'gender': '', 'priority': 41}},
        {'speaker': 'p281', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P281', 'gender': '', 'priority': 41}},
        {'speaker': 'p277', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P277', 'gender': '', 'priority': 41}},
        {'speaker': 'p231', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P231', 'gender': '', 'priority': 41}},
        {'speaker': 'p238', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P238', 'gender': '', 'priority': 41}},
        {'speaker': 'p271', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P271', 'gender': '', 'priority': 41}},
        {'speaker': 'p257', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P257', 'gender': '', 'priority': 41}},
        {'speaker': 'p273', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P273', 'gender': '', 'priority': 41}},
        {'speaker': 'p284', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P284', 'gender': '', 'priority': 41}},
        {'speaker': 'p329', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P329', 'gender': '', 'priority': 41}},
        {'speaker': 'p361', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P361', 'gender': '', 'priority': 41}},
        {'speaker': 'p287', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P287', 'gender': '', 'priority': 41}},
        {'speaker': 'p360', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P360', 'gender': '', 'priority': 41}},
        {'speaker': 'p374', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P374', 'gender': '', 'priority': 41}},
        {'speaker': 'p376', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P376', 'gender': '', 'priority': 41}},
        {'speaker': 'p310', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P310', 'gender': '', 'priority': 41}},
        {'speaker': 'p304', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P304', 'gender': '', 'priority': 41}},
        {'speaker': 'p340', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P340', 'gender': '', 'priority': 41}},
        {'speaker': 'p347', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P347', 'gender': '', 'priority': 41}},
        {'speaker': 'p330', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P330', 'gender': '', 'priority': 41}},
        {'speaker': 'p308', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P308', 'gender': '', 'priority': 41}},
        {'speaker': 'p314', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P314', 'gender': '', 'priority': 41}},
        {'speaker': 'p317', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P317', 'gender': '', 'priority': 41}},
        {'speaker': 'p339', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P339', 'gender': '', 'priority': 41}},
        {'speaker': 'p311', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P311', 'gender': '', 'priority': 41}},
        {'speaker': 'p294', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P294', 'gender': '', 'priority': 41}},
        {'speaker': 'p305', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P305', 'gender': '', 'priority': 41}},
        {'speaker': 'p266', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P266', 'gender': '', 'priority': 41}},
        {'speaker': 'p335', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P335', 'gender': '', 'priority': 41}},
        {'speaker': 'p334', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P334', 'gender': '', 'priority': 41}},
        {'speaker': 'p318', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P318', 'gender': '', 'priority': 41}},
        {'speaker': 'p323', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P323', 'gender': '', 'priority': 41}},
        {'speaker': 'p351', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P351', 'gender': '', 'priority': 41}},
        {'speaker': 'p333', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P333', 'gender': '', 'priority': 41}},
        {'speaker': 'p313', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P313', 'gender': '', 'priority': 41}},
        {'speaker': 'p316', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P316', 'gender': '', 'priority': 41}},
        {'speaker': 'p244', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P244', 'gender': '', 'priority': 41}},
        {'speaker': 'p307', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P307', 'gender': '', 'priority': 41}},
        {'speaker': 'p363', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P363', 'gender': '', 'priority': 41}},
        {'speaker': 'p336', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P336', 'gender': '', 'priority': 41}},
        {'speaker': 'p312', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P312', 'gender': '', 'priority': 41}},
        {'speaker': 'p267', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P267', 'gender': '', 'priority': 41}},
        {'speaker': 'p297', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P297', 'gender': '', 'priority': 41}},
        {'speaker': 'p275', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P275', 'gender': '', 'priority': 41}},
        {'speaker': 'p295', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P295', 'gender': '', 'priority': 41}},
        {'speaker': 'p288', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P288', 'gender': '', 'priority': 41}},
        {'speaker': 'p258', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P258', 'gender': '', 'priority': 41}},
        {'speaker': 'p301', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P301', 'gender': '', 'priority': 41}},
        {'speaker': 'p232', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P232', 'gender': '', 'priority': 41}},
        {'speaker': 'p292', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P292', 'gender': '', 'priority': 41}},
        {'speaker': 'p272', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P272', 'gender': '', 'priority': 41}},
        {'speaker': 'p278', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P278', 'gender': '', 'priority': 41}},
        {'speaker': 'p280', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P280', 'gender': '', 'priority': 41}},
        {'speaker': 'p341', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P341', 'gender': '', 'priority': 41}},
        {'speaker': 'p268', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P268', 'gender': '', 'priority': 41}},
        {'speaker': 'p298', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P298', 'gender': '', 'priority': 41}},
        {'speaker': 'p299', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P299', 'gender': '', 'priority': 41}},
        {'speaker': 'p279', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P279', 'gender': '', 'priority': 41}},
        {'speaker': 'p285', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P285', 'gender': '', 'priority': 41}},
        {'speaker': 'p326', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P326', 'gender': '', 'priority': 41}},
        {'speaker': 'p300', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P300', 'gender': '', 'priority': 41}},
        {'speaker': 's5', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - S5', 'gender': '', 'priority': 41}},
        {'speaker': 'p230', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P230', 'gender': '', 'priority': 41}},
        {'speaker': 'p254', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P254', 'gender': '', 'priority': 41}},
        {'speaker': 'p269', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P269', 'gender': '', 'priority': 41}},
        {'speaker': 'p293', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P293', 'gender': '', 'priority': 41}},
        {'speaker': 'p252', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P252', 'gender': '', 'priority': 41}},
        {'speaker': 'p345', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P345', 'gender': '', 'priority': 41}},
        {'speaker': 'p262', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P262', 'gender': '', 'priority': 41}},
        {'speaker': 'p243', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P243', 'gender': '', 'priority': 41}},
        {'speaker': 'p227', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P227', 'gender': '', 'priority': 41}},
        {'speaker': 'p343', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P343', 'gender': '', 'priority': 41}},
        {'speaker': 'p255', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P255', 'gender': '', 'priority': 41}},
        {'speaker': 'p229', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P229', 'gender': '', 'priority': 41}},
        {'speaker': 'p240', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P240', 'gender': '', 'priority': 41}},
        {'speaker': 'p248', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P248', 'gender': '', 'priority': 41}},
        {'speaker': 'p253', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P253', 'gender': '', 'priority': 41}},
        {'speaker': 'p233', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P233', 'gender': '', 'priority': 41}},
        {'speaker': 'p228', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P228', 'gender': '', 'priority': 41}},
        {'speaker': 'p251', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P251', 'gender': '', 'priority': 41}},
        {'speaker': 'p282', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P282', 'gender': '', 'priority': 41}},
        {'speaker': 'p246', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P246', 'gender': '', 'priority': 41}},
        {'speaker': 'p234', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P234', 'gender': '', 'priority': 41}},
        {'speaker': 'p226', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P226', 'gender': '', 'priority': 41}},
        {'speaker': 'p260', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P260', 'gender': '', 'priority': 41}},
        {'speaker': 'p245', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P245', 'gender': '', 'priority': 41}},
        {'speaker': 'p241', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P241', 'gender': '', 'priority': 41}},
        {'speaker': 'p303', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P303', 'gender': '', 'priority': 41}},
        {'speaker': 'p265', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P265', 'gender': '', 'priority': 41}},
        {'speaker': 'p306', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P306', 'gender': '', 'priority': 41}},
        {'speaker': 'p237', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P237', 'gender': '', 'priority': 41}},
        {'speaker': 'p249', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P249', 'gender': '', 'priority': 41}},
        {'speaker': 'p256', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P256', 'gender': '', 'priority': 41}},
        {'speaker': 'p302', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P302', 'gender': '', 'priority': 41}},
        {'speaker': 'p364', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P364', 'gender': '', 'priority': 41}},
        {'speaker': 'p225', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P225', 'gender': '', 'priority': 41}},
        {'speaker': 'p362', 'voice': 'en_US/vctk_low',
         'meta': {'offline': False, 'display_name': 'Vctk - P362', 'gender': '', 'priority': 41}}],
    'es-es': [
        {'speaker': 'default', 'voice': 'es_ES/carlfm_low',
         'meta': {'offline': False, 'display_name': 'Carlfm', 'gender': '', 'priority': 40}},
        {'speaker': 'tux', 'voice': 'es_ES/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Tux', 'gender': '', 'priority': 40}},
        {'speaker': 'victor_villarraza', 'voice': 'es_ES/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Victor Villarraza', 'gender': '', 'priority': 40}},
        {'speaker': 'karen_savage', 'voice': 'es_ES/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Karen Savage', 'gender': '', 'priority': 40}}],
    'fa': [
        {'speaker': 'default', 'voice': 'fa/haaniye_low',
         'meta': {'offline': False, 'display_name': 'Haaniye', 'gender': '', 'priority': 50}}],
    'fi-fi': [
        {'speaker': 'default', 'voice': 'fi_FI/harri-tapani-ylilammi_low',
         'meta': {'offline': False, 'display_name': 'Harri-Tapani-Ylilammi', 'gender': '', 'priority': 50}}],
    'fr-fr': [
        {'speaker': 'ezwa', 'voice': 'fr_FR/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Ezwa', 'gender': '', 'priority': 40}},
        {'speaker': 'nadine_eckert_boulet', 'voice': 'fr_FR/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Nadine Eckert Boulet', 'gender': '', 'priority': 40}},
        {'speaker': 'bernard', 'voice': 'fr_FR/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Bernard', 'gender': '', 'priority': 40}},
        {'speaker': 'zeckou', 'voice': 'fr_FR/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Zeckou', 'gender': '', 'priority': 40}},
        {'speaker': 'gilles_g_le_blanc', 'voice': 'fr_FR/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Gilles G Le Blanc', 'gender': '', 'priority': 40}},
        {'speaker': 'default', 'voice': 'fr_FR/siwis_low',
         'meta': {'offline': False, 'display_name': 'Siwis', 'gender': '', 'priority': 40}},
        {'speaker': 'default', 'voice': 'fr_FR/tom_low',
         'meta': {'offline': False, 'display_name': 'Tom', 'gender': '', 'priority': 40}}],
    'gu-in': [
        {'speaker': 'cmu_indic_guj_dp', 'voice': 'gu_IN/cmu-indic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Indic - Cmu Indic Guj Dp', 'gender': '', 'priority': 50}},
        {'speaker': 'cmu_indic_guj_ad', 'voice': 'gu_IN/cmu-indic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Indic - Cmu Indic Guj Ad', 'gender': '', 'priority': 50}},
        {'speaker': 'cmu_indic_guj_kt', 'voice': 'gu_IN/cmu-indic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Indic - Cmu Indic Guj Kt', 'gender': '', 'priority': 50}}],
    'ha-ne': [{'speaker': 'default', 'voice': 'ha_NE/openbible_low',
               'meta': {'offline': False, 'display_name': 'Openbible', 'gender': '', 'priority': 50}}],
    'hu-hu': [
        {'speaker': 'default', 'voice': 'hu_HU/diana-majlinger_low',
         'meta': {'offline': False, 'display_name': 'Diana-Majlinger', 'gender': '', 'priority': 50}}],
    'it-it': [
        {'speaker': 'default', 'voice': 'it_IT/riccardo-fasol_low',
         'meta': {'offline': False, 'display_name': 'Riccardo-Fasol', 'gender': '', 'priority': 40}},
        {'speaker': '1595', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 1595', 'gender': '', 'priority': 50}},
        {'speaker': '4974', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 4974', 'gender': '', 'priority': 50}},
        {'speaker': '4998', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 4998', 'gender': '', 'priority': 50}},
        {'speaker': '6807', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 6807', 'gender': '', 'priority': 50}},
        {'speaker': '1989', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 1989', 'gender': '', 'priority': 50}},
        {'speaker': '2033', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 2033', 'gender': '', 'priority': 50}},
        {'speaker': '2019', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 2019', 'gender': '', 'priority': 50}},
        {'speaker': '659', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 659', 'gender': '', 'priority': 50}},
        {'speaker': '4649', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 4649', 'gender': '', 'priority': 50}},
        {'speaker': '9772', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 9772', 'gender': '', 'priority': 50}},
        {'speaker': '1725', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 1725', 'gender': '', 'priority': 50}},
        {'speaker': '10446', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 10446', 'gender': '', 'priority': 50}},
        {'speaker': '6348', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 6348', 'gender': '', 'priority': 50}},
        {'speaker': '6001', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 6001', 'gender': '', 'priority': 50}},
        {'speaker': '9185', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 9185', 'gender': '', 'priority': 50}},
        {'speaker': '8842', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 8842', 'gender': '', 'priority': 50}},
        {'speaker': '8828', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 8828', 'gender': '', 'priority': 50}},
        {'speaker': '12428', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 12428', 'gender': '', 'priority': 50}},
        {'speaker': '8181', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 8181', 'gender': '', 'priority': 50}},
        {'speaker': '7440', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 7440', 'gender': '', 'priority': 50}},
        {'speaker': '8207', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 8207', 'gender': '', 'priority': 50}},
        {'speaker': '277', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 277', 'gender': '', 'priority': 50}},
        {'speaker': '5421', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 5421', 'gender': '', 'priority': 50}},
        {'speaker': '12804', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 12804', 'gender': '', 'priority': 50}},
        {'speaker': '4705', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 4705', 'gender': '', 'priority': 50}},
        {'speaker': '7936', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 7936', 'gender': '', 'priority': 50}},
        {'speaker': '844', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 844', 'gender': '', 'priority': 50}},
        {'speaker': '6299', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 6299', 'gender': '', 'priority': 50}},
        {'speaker': '644', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 644', 'gender': '', 'priority': 50}},
        {'speaker': '8384', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 8384', 'gender': '', 'priority': 50}},
        {'speaker': '1157', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 1157', 'gender': '', 'priority': 50}},
        {'speaker': '7444', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 7444', 'gender': '', 'priority': 50}},
        {'speaker': '643', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 643', 'gender': '', 'priority': 50}},
        {'speaker': '4971', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 4971', 'gender': '', 'priority': 50}},
        {'speaker': '4975', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 4975', 'gender': '', 'priority': 50}},
        {'speaker': '6744', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 6744', 'gender': '', 'priority': 50}},
        {'speaker': '8461', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 8461', 'gender': '', 'priority': 50}},
        {'speaker': '7405', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 7405', 'gender': '', 'priority': 50}},
        {'speaker': '5010', 'voice': 'it_IT/mls_low',
         'meta': {'offline': False, 'display_name': 'Mls - 5010', 'gender': '', 'priority': 50}}],
    'jv-id': [
        {'speaker': '07875', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 07875', 'gender': '', 'priority': 50}},
        {'speaker': '05522', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 05522', 'gender': '', 'priority': 50}},
        {'speaker': '03424', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 03424', 'gender': '', 'priority': 50}},
        {'speaker': '06510', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 06510', 'gender': '', 'priority': 50}},
        {'speaker': '03314', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 03314', 'gender': '', 'priority': 50}},
        {'speaker': '03187', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 03187', 'gender': '', 'priority': 50}},
        {'speaker': '07638', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 07638', 'gender': '', 'priority': 50}},
        {'speaker': '06207', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 06207', 'gender': '', 'priority': 50}},
        {'speaker': '08736', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 08736', 'gender': '', 'priority': 50}},
        {'speaker': '04679', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 04679', 'gender': '', 'priority': 50}},
        {'speaker': '01392', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 01392', 'gender': '', 'priority': 50}},
        {'speaker': '05540', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 05540', 'gender': '', 'priority': 50}},
        {'speaker': '05219', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 05219', 'gender': '', 'priority': 50}},
        {'speaker': '00027', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 00027', 'gender': '', 'priority': 50}},
        {'speaker': '00264', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 00264', 'gender': '', 'priority': 50}},
        {'speaker': '09724', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 09724', 'gender': '', 'priority': 50}},
        {'speaker': '04588', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 04588', 'gender': '', 'priority': 50}},
        {'speaker': '09039', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 09039', 'gender': '', 'priority': 50}},
        {'speaker': '04285', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 04285', 'gender': '', 'priority': 50}},
        {'speaker': '05970', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 05970', 'gender': '', 'priority': 50}},
        {'speaker': '08305', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 08305', 'gender': '', 'priority': 50}},
        {'speaker': '04982', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 04982', 'gender': '', 'priority': 50}},
        {'speaker': '08002', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 08002', 'gender': '', 'priority': 50}},
        {'speaker': '06080', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 06080', 'gender': '', 'priority': 50}},
        {'speaker': '07765', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 07765', 'gender': '', 'priority': 50}},
        {'speaker': '02326', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 02326', 'gender': '', 'priority': 50}},
        {'speaker': '03727', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 03727', 'gender': '', 'priority': 50}},
        {'speaker': '04175', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 04175', 'gender': '', 'priority': 50}},
        {'speaker': '06383', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 06383', 'gender': '', 'priority': 50}},
        {'speaker': '02884', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 02884', 'gender': '', 'priority': 50}},
        {'speaker': '06941', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 06941', 'gender': '', 'priority': 50}},
        {'speaker': '08178', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 08178', 'gender': '', 'priority': 50}},
        {'speaker': '00658', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 00658', 'gender': '', 'priority': 50}},
        {'speaker': '04715', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 04715', 'gender': '', 'priority': 50}},
        {'speaker': '05667', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 05667', 'gender': '', 'priority': 50}},
        {'speaker': '01519', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 01519', 'gender': '', 'priority': 50}},
        {'speaker': '07335', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 07335', 'gender': '', 'priority': 50}},
        {'speaker': '02059', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 02059', 'gender': '', 'priority': 50}},
        {'speaker': '01932', 'voice': 'jv_ID/google-gmu_low',
         'meta': {'offline': False, 'display_name': 'Google-Gmu - 01932', 'gender': '', 'priority': 50}}],
    'ko-ko': [
        {'speaker': 'default', 'voice': 'ko_KO/kss_low',
         'meta': {'offline': False, 'display_name': 'Kss', 'gender': '', 'priority': 50}}],
    'ne-np': [
        {'speaker': '0546', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 0546', 'gender': '', 'priority': 50}},
        {'speaker': '3614', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 3614', 'gender': '', 'priority': 50}},
        {'speaker': '2099', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 2099', 'gender': '', 'priority': 50}},
        {'speaker': '3960', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 3960', 'gender': '', 'priority': 50}},
        {'speaker': '6834', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 6834', 'gender': '', 'priority': 50}},
        {'speaker': '7957', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 7957', 'gender': '', 'priority': 50}},
        {'speaker': '6329', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 6329', 'gender': '', 'priority': 50}},
        {'speaker': '9407', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 9407', 'gender': '', 'priority': 50}},
        {'speaker': '6587', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 6587', 'gender': '', 'priority': 50}},
        {'speaker': '0258', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 0258', 'gender': '', 'priority': 50}},
        {'speaker': '2139', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 2139', 'gender': '', 'priority': 50}},
        {'speaker': '5687', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 5687', 'gender': '', 'priority': 50}},
        {'speaker': '0283', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 0283', 'gender': '', 'priority': 50}},
        {'speaker': '3997', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 3997', 'gender': '', 'priority': 50}},
        {'speaker': '3154', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 3154', 'gender': '', 'priority': 50}},
        {'speaker': '0883', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 0883', 'gender': '', 'priority': 50}},
        {'speaker': '2027', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 2027', 'gender': '', 'priority': 50}},
        {'speaker': '0649', 'voice': 'ne_NP/ne-google_low',
         'meta': {'offline': False, 'display_name': 'Ne-Google - 0649', 'gender': '', 'priority': 50}}],
    'nl': [
        {'speaker': 'default', 'voice': 'nl/bart-de-leeuw_low',
         'meta': {'offline': False, 'display_name': 'Bart-De-Leeuw', 'gender': '', 'priority': 40}},
        {'speaker': 'default', 'voice': 'nl/flemishguy_low',
         'meta': {'offline': False, 'display_name': 'Flemishguy', 'gender': '', 'priority': 40}},
        {'speaker': 'default', 'voice': 'nl/nathalie_low',
         'meta': {'offline': False, 'display_name': 'Nathalie', 'gender': '', 'priority': 40}},
        {'speaker': 'default', 'voice': 'nl/pmk_low',
         'meta': {'offline': False, 'display_name': 'Pmk', 'gender': '', 'priority': 50}},
        {'speaker': 'default', 'voice': 'nl/rdh_low',
         'meta': {'offline': False, 'display_name': 'Rdh', 'gender': '', 'priority': 50}}],
    'pl-pl': [
        {'speaker': 'piotr_nater', 'voice': 'pl_PL/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Piotr Nater', 'gender': '', 'priority': 40}},
        {'speaker': 'nina_brown', 'voice': 'pl_PL/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Nina Brown', 'gender': '', 'priority': 40}}],
    'ru-ru': [
        {'speaker': 'hajdurova', 'voice': 'ru_RU/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - Hajdurova', 'gender': '', 'priority': 50}},
        {'speaker': 'minaev', 'voice': 'ru_RU/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - Minaev', 'gender': '', 'priority': 50}},
        {'speaker': 'nikolaev', 'voice': 'ru_RU/multi_low',
         'meta': {'offline': False, 'display_name': 'Multi - Nikolaev', 'gender': '', 'priority': 50}}],
    'sw': [
        {'speaker': 'default', 'voice': 'sw/lanfrica_low',
         'meta': {'offline': False, 'display_name': 'Lanfrica', 'gender': '', 'priority': 50}}],
    'te-in': [
        {'speaker': 'ss', 'voice': 'te_IN/cmu-indic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Indic - Ss', 'gender': '', 'priority': 50}},
        {'speaker': 'sk', 'voice': 'te_IN/cmu-indic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Indic - Sk', 'gender': '', 'priority': 50}},
        {'speaker': 'kpn', 'voice': 'te_IN/cmu-indic_low',
         'meta': {'offline': False, 'display_name': 'Cmu-Indic - Kpn', 'gender': '', 'priority': 50}}],
    'tn-za': [
        {'speaker': '1932', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 1932', 'gender': '', 'priority': 50}},
        {'speaker': '0045', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 0045', 'gender': '', 'priority': 50}},
        {'speaker': '3342', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 3342', 'gender': '', 'priority': 50}},
        {'speaker': '4850', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 4850', 'gender': '', 'priority': 50}},
        {'speaker': '6206', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 6206', 'gender': '', 'priority': 50}},
        {'speaker': '3629', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 3629', 'gender': '', 'priority': 50}},
        {'speaker': '9061', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 9061', 'gender': '', 'priority': 50}},
        {'speaker': '6116', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 6116', 'gender': '', 'priority': 50}},
        {'speaker': '7674', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 7674', 'gender': '', 'priority': 50}},
        {'speaker': '0378', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 0378', 'gender': '', 'priority': 50}},
        {'speaker': '5628', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 5628', 'gender': '', 'priority': 50}},
        {'speaker': '8333', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8333', 'gender': '', 'priority': 50}},
        {'speaker': '8512', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8512', 'gender': '', 'priority': 50}},
        {'speaker': '0441', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 0441', 'gender': '', 'priority': 50}},
        {'speaker': '6459', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 6459', 'gender': '', 'priority': 50}},
        {'speaker': '4506', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 4506', 'gender': '', 'priority': 50}},
        {'speaker': '7866', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 7866', 'gender': '', 'priority': 50}},
        {'speaker': '8532', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8532', 'gender': '', 'priority': 50}},
        {'speaker': '2839', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 2839', 'gender': '', 'priority': 50}},
        {'speaker': '7896', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 7896', 'gender': '', 'priority': 50}},
        {'speaker': '1498', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 1498', 'gender': '', 'priority': 50}},
        {'speaker': '1483', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 1483', 'gender': '', 'priority': 50}},
        {'speaker': '8914', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 8914', 'gender': '', 'priority': 50}},
        {'speaker': '6234', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 6234', 'gender': '', 'priority': 50}},
        {'speaker': '9365', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 9365', 'gender': '', 'priority': 50}},
        {'speaker': '7693', 'voice': 'tn_ZA/google-nwu_low',
         'meta': {'offline': False, 'display_name': 'Google-Nwu - 7693', 'gender': '', 'priority': 50}}],
    'uk-uk': [
        {'speaker': 'obruchov', 'voice': 'uk_UK/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Obruchov', 'gender': '', 'priority': 40}},
        {'speaker': 'shepel', 'voice': 'uk_UK/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Shepel', 'gender': '', 'priority': 40}},
        {'speaker': 'loboda', 'voice': 'uk_UK/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Loboda', 'gender': '', 'priority': 40}},
        {'speaker': 'miskun', 'voice': 'uk_UK/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Miskun', 'gender': '', 'priority': 40}},
        {'speaker': 'sumska', 'voice': 'uk_UK/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Sumska', 'gender': '', 'priority': 40}},
        {'speaker': 'pysariev', 'voice': 'uk_UK/m-ailabs_low',
         'meta': {'offline': False, 'display_name': 'M-Ailabs - Pysariev', 'gender': '', 'priority': 40}}],
    'vi-vn': [
        {'speaker': 'default', 'voice': 'vi_VN/vais1000_low',
         'meta': {'offline': False, 'display_name': 'Vais1000', 'gender': '', 'priority': 50}}],
    'yo': [
        {'speaker': 'default', 'voice': 'yo/openbible_low',
         'meta': {'offline': False, 'display_name': 'Openbible', 'gender': '', 'priority': 50}}]}

if __name__ == "__main__":
    tt = Mimic3ServerTTSPlugin()
    tt.get_tts("hello world", "test.wav", lang="en-gb")
    tt.get_tts("hello world", "test3.wav", voice="en_US/cmu-arctic_low", speaker="slt")
    tt.get_tts("hello world", "test4.wav", voice="en_US/cmu-arctic_low#lnh")
    tt.get_tts("hello world", "test5.wav", voice="cmu-arctic_low#rms", lang="en-us")
