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
import base64
import math
import random
import re

import requests

from ovos_plugin_manager.templates.tts import TTS, TTSValidator, RemoteTTSException
from ovos_utils.lang.visimes import VISIMES


class Mimic2TTSPlugin(TTS):
    """Interface to Mimic2 TTS."""
    # Heuristic value, caps character length of a chunk of text
    # to be spoken as a work around for current Tacotron implementation limits.
    max_sentence_size = 170

    def __init__(self, lang="en-us", config=None):
        config = config or {}
        super(Mimic2TTSPlugin, self).__init__(lang, config,
                                              Mimic2TTSValidator(self), 'wav')
        self.voice = self.voice.lower()
        self._visemes = False
        if self.config.get("url"):  # self hosted
            self.url = self.config["url"]
            # TODO disable cache to avoid filename conflicts with other voices
            if not self.voice or self.voice == "default":
                self.voice = f"selfhosted{random.randint(0, 9999999)}"
                self.cache.persist = False
        elif self.voice == "kusal" or self.voice == "default":
            self.url = "https://mimic-api.mycroft.ai/synthesize"
            self._visemes = True
        elif self.voice == "nancy":
            self.url = "https://nancy.2022.us/synthesize"
            self.cache.persist = True  # always save synths to persistent cache
        elif self.voice == "ljspeech":
            self.url = "https://ljspeech.2022.us/synthesize"
            self.cache.persist = True  # always save synths to persistent cache
        else:
            self.voice = "kusal"
            self.url = "https://mimic-api.mycroft.ai/synthesize"

    def get_tts(self, sentence, wav_file, lang=None):
        """Fetch tts audio using tacotron endpoint.

        Arguments:
            sentence (str): Sentence to generate audio for
            wav_file (str): output file path
        Returns:
            Tuple ((str) written file, None)
        """
        params = {"text": sentence, "visimes": self._visemes}
        r = requests.get(self.url, params=params)
        if not r.ok:
            raise RemoteTTSException(f"Mimic2 server error: {r.reason}")
        if not self._visemes:
            audio_data = r.content
            phonemes = None
        else:
            results = r.json()
            audio_data = base64.b64decode(results['audio_base64'])
            phonemes = results['visimes']
        with open(wav_file, "wb") as f:
            f.write(audio_data)
        return (wav_file, phonemes)  # No phonemes

    def viseme(self, phonemes):
        """Maps phonemes to appropriate viseme encoding

        Arguments:
            phonemes (list): list of tuples (phoneme, time_start)

        Returns:
            list: list of tuples (viseme_encoding, time_start)
        """
        visemes = []
        for pair in phonemes:
            if pair[0]:
                phone = pair[0].lower()
            else:
                # if phoneme doesn't exist use
                # this as placeholder since it
                # is the most common one "3"
                phone = 'z'
            vis = VISIMES.get(phone)
            vis_dur = float(pair[1])
            visemes.append((vis, vis_dur))
        return visemes

    @property
    def available_languages(self) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set(Mimic2TTSPluginConfig.keys())

    # below are helpers to split sentence in chunks that tacotron can synth
    # there is a limit for 150 chars
    def _preprocess_sentence(self, sentence):
        """Split sentence in chunks better suited for mimic2. """
        return self._split_sentences(sentence)

    @staticmethod
    def _split_sentences(text):
        """Split text into smaller chunks for TTS generation.
        NOTE: The smaller chunks are needed due to current Catotron TTS limitations.
        This stage can be removed once Catotron can generate longer sentences.
        Arguments:
            text (str): text to split
            chunk_size (int): size of each chunk
            split_by_punc (bool, optional): Defaults to True.
        Returns:
            list: list of text chunks
        """
        if len(text) <= Mimic2TTSPlugin.max_sentence_size:
            return [Mimic2TTSPlugin._add_punctuation(text)]

        # first split by punctuations that are major pauses
        first_splits = Mimic2TTSPlugin._split_by_punctuation(
            text,
            puncs=[r'\.', r'\!', r'\?', r'\:', r'\;']
        )

        # if chunks are too big, split by minor pauses (comma, hyphen)
        second_splits = []
        for chunk in first_splits:
            if len(chunk) > Mimic2TTSPlugin.max_sentence_size:
                second_splits += Mimic2TTSPlugin._split_by_punctuation(
                    chunk, puncs=[r'\,', '--', '-'])
            else:
                second_splits.append(chunk)

        # if chunks are still too big, chop into pieces of at most 20 words
        third_splits = []
        for chunk in second_splits:
            if len(chunk) > Mimic2TTSPlugin.max_sentence_size:
                third_splits += Mimic2TTSPlugin._split_by_chunk_size(
                    chunk, 20)
            else:
                third_splits.append(chunk)

        return [Mimic2TTSPlugin._add_punctuation(chunk)
                for chunk in third_splits]

    @staticmethod
    def _break_chunks(l, n):
        """Yield successive n-sized chunks
        Arguments:
            l (list): text (str) to split
            chunk_size (int): chunk size
        """
        for i in range(0, len(l), n):
            yield " ".join(l[i:i + n])

    @staticmethod
    def _split_by_chunk_size(text, chunk_size):
        """Split text into word chunks by chunk_size size
        Arguments:
            text (str): text to split
            chunk_size (int): chunk size
        Returns:
            list: list of text chunks
        """
        text_list = text.split()

        if len(text_list) <= chunk_size:
            return [text]

        if chunk_size < len(text_list) < (chunk_size * 2):
            return list(Mimic2TTSPlugin._break_chunks(
                text_list,
                int(math.ceil(len(text_list) / 2))
            ))
        elif (chunk_size * 2) < len(text_list) < (chunk_size * 3):
            return list(Mimic2TTSPlugin._break_chunks(
                text_list,
                int(math.ceil(len(text_list) / 3))
            ))
        elif (chunk_size * 3) < len(text_list) < (chunk_size * 4):
            return list(Mimic2TTSPlugin._break_chunks(
                text_list,
                int(math.ceil(len(text_list) / 4))
            ))
        else:
            return list(Mimic2TTSPlugin._break_chunks(
                text_list,
                int(math.ceil(len(text_list) / 5))
            ))

    @staticmethod
    def _split_by_punctuation(chunks, puncs):
        """Splits text by various punctionations
        e.g. hello, world => [hello, world]
        Arguments:
            chunks (list or str): text (str) to split
            puncs (list): list of punctuations used to split text
        Returns:
            list: list with split text
        """
        if isinstance(chunks, str):
            out = [chunks]
        else:
            out = chunks

        for punc in puncs:
            splits = []
            for t in out:
                # Split text by punctuation, but not embedded punctuation.  E.g.
                # Split:  "Short sentence.  Longer sentence."
                # But not at: "I.B.M." or "3.424", "3,424" or "what's-his-name."
                splits += re.split(r'(?<!\.\S)' + punc + r'\s', t)
            out = splits
        return [t.strip() for t in out]

    @staticmethod
    def _add_punctuation(text):
        """Add punctuation at the end of each chunk.
        Catotron expects some form of punctuation at the end of a sentence.
        """
        punctuation = ['.', '?', '!', ';']
        if len(text) >= 1 and text[-1] not in punctuation:
            return text + ', '
        else:
            return text


class Mimic2TTSValidator(TTSValidator):
    def __init__(self, tts):
        super(Mimic2TTSValidator, self).__init__(tts)

    def validate_lang(self):
        lang = self.tts.lang.lower()
        assert lang.startswith("en")

    def validate_connection(self):
        pass

    def get_tts_class(self):
        return Mimic2TTSPlugin


Mimic2TTSPluginConfig = {
    "en-us": [
        {"voice": "kusal", "gender": "male", "display_name": "Kusal", "offline": False, "priority": 45},
        {"voice": "nancy", "gender": "female", "display_name": "Nancy", "offline": False, "priority": 90},
        {"voice": "ljspeech", "gender": "female", "display_name": "LJSpeech", "offline": False, "priority": 90}
    ]
}
