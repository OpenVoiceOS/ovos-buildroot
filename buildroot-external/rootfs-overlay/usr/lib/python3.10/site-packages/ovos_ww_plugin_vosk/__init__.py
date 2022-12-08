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
import enum
import json
from os.path import join, exists
from ovos_utils.messagebus import get_mycroft_bus, Message
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from ovos_skill_installer import download_extract_zip, download_extract_tar
from ovos_utils.log import LOG
from ovos_utils.parse import fuzzy_match, MatchStrategy
from ovos_utils.xdg_utils import xdg_data_home
from speech_recognition import AudioData
from vosk import Model as KaldiModel, KaldiRecognizer


class MatchRule(str, enum.Enum):
    CONTAINS = "contains"
    EQUALS = "equals"
    STARTS = "starts"
    ENDS = "ends"
    FUZZY = "fuzzy"
    TOKEN_SET_RATIO = "token_set_ratio"
    TOKEN_SORT_RATIO = "token_sort_ratio"
    PARTIAL_TOKEN_SET_RATIO = "partial_token_set_ratio"
    PARTIAL_TOKEN_SORT_RATIO = "partial_token_sort_ratio"


class ModelContainer:
    UNK = "[unk]"

    def __init__(self, samples=None, full_vocab=False):
        if not full_vocab and not samples:
            full_vocab = True
        samples = samples or []
        if self.UNK not in samples:
            samples.append(self.UNK)
        self.samples = samples
        self.full_vocab = full_vocab
        self.engine = None

    def get_engine(self, lang=None):
        if not self.engine and lang:
            lang = lang.split("-")[0].lower()
            self.load_language(lang)
        return self.engine

    def get_partial_transcription(self, lang=None):
        engine = self.get_engine(lang)
        res = engine.PartialResult()
        return json.loads(res)["partial"]

    def get_final_transcription(self, lang=None):
        engine = self.get_engine(lang)
        res = engine.FinalResult()
        return json.loads(res)["text"]

    def process_audio(self, audio, lang=None):
        engine = self.get_engine(lang)
        if isinstance(audio, AudioData):
            audio = audio.get_wav_data()
        return engine.AcceptWaveform(audio)

    def get_model(self, model_path, samples=None):
        if model_path:
            if self.full_vocab:
                model = KaldiRecognizer(KaldiModel(model_path), 16000)
            else:
                model = KaldiRecognizer(KaldiModel(model_path), 16000,
                                        json.dumps(samples or self.samples))
            return model
        else:
            raise FileNotFoundError

    def load_model(self, model_path):
        self.engine = self.get_model(model_path, self.samples)

    def load_language(self, lang):
        lang = lang.split("-")[0].lower()
        model_path = self.download_language(lang)
        self.load_model(model_path)

    @staticmethod
    def download_language(lang):
        lang = lang.split("-")[0].lower()
        model_path = ModelContainer.lang2modelurl(lang)
        if model_path and model_path.startswith("http"):
            model_path = ModelContainer.download_model(model_path)
        return model_path

    @staticmethod
    def download_model(url):
        folder = join(xdg_data_home(), 'vosk')
        name = url.split("/")[-1].split(".")[0]
        model_path = join(folder, name)
        if not exists(model_path):
            LOG.info(f"Downloading model for vosk {url}")
            LOG.info("this might take a while")
            if url.endswith(".zip"):
                download_extract_zip(url, folder=folder, skill_folder_name=name)
            else:
                download_extract_tar(url, folder=folder, skill_folder_name=name)
            LOG.info(f"Model downloaded to {model_path}")

        return model_path

    @staticmethod
    def lang2modelurl(lang, small=True):
        lang2url = {
            "en": "http://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "en-in": "http://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip",
            "cn": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.3.zip",
            "ru": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.15.zip",
            "fr": "https://alphacephei.com/vosk/models/vosk-model-small-fr-pguyot-0.3.zip",
            "de": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
            "es": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.3.zip",
            "pt": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
            "gr": "https://alphacephei.com/vosk/models/vosk-model-el-gr-0.7.zip",
            "tr": "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip",
            "vn": "https://alphacephei.com/vosk/models/vosk-model-small-vn-0.3.zip",
            "it": "https://alphacephei.com/vosk/models/vosk-model-small-it-0.4.zip",
            "nl": "https://alphacephei.com/vosk/models/vosk-model-nl-spraakherkenning-0.6-lgraph.zip",
            "ca": "https://alphacephei.com/vosk/models/vosk-model-small-ca-0.4.zip",
            "ar": "https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip",
            "fa": "https://alphacephei.com/vosk/models/vosk-model-small-fa-0.5.zip",
            "tl": "https://alphacephei.com/vosk/models/vosk-model-tl-ph-generic-0.6.zip"
        }
        biglang2url = {
            "en": "https://alphacephei.com/vosk/models/vosk-model-en-us-aspire-0.2.zip",
            "en-in": "http://alphacephei.com/vosk/models/vosk-model-en-in-0.4.zip",
            "cn": "https://alphacephei.com/vosk/models/vosk-model-cn-0.1.zip",
            "ru": "https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip",
            "fr": "https://github.com/pguyot/zamia-speech/releases/download/20190930/kaldi-generic-fr-tdnn_f-r20191016.tar.xz",
            "de": "https://alphacephei.com/vosk/models/vosk-model-de-0.6.zip",
            "nl": "https://alphacephei.com/vosk/models/vosk-model-nl-spraakherkenning-0.6.zip",
            "fa": "https://alphacephei.com/vosk/models/vosk-model-fa-0.5.zip"

        }
        if not small:
            lang2url.update(biglang2url)
        lang = lang.lower()
        if lang in lang2url:
            return lang2url[lang]
        lang = lang.split("-")[0]
        return lang2url.get(lang)


class VoskWakeWordPlugin(HotWordEngine):
    """Vosk Wake Word"""
    # Hard coded values in mycroft/client/speech/mic.py
    SEC_BETWEEN_WW_CHECKS = 0.2
    MAX_EXPECTED_DURATION = 3  # seconds of data chunks received at a time

    def __init__(self, hotword="hey mycroft", config=None, lang="en-us"):
        config = config or {}
        super(VoskWakeWordPlugin, self).__init__(hotword, config, lang)
        default_sample = [hotword.replace("_", " ").replace("-", " ")]
        self.full_vocab = self.config.get("full_vocab", False)
        self.samples = self.config.get("samples", default_sample)
        self.rule = self.config.get("rule", MatchRule.EQUALS)
        self.thresh = self.config.get("threshold", 0.75)
        self.debug = self.config.get("debug", False)
        self.time_between_checks = \
            min(self.config.get("time_between_checks", 1.0), 3)
        self.expected_duration = self.MAX_EXPECTED_DURATION
        self._counter = 0
        self._load_model()

    def _load_model(self):
        # model_folder for backwards compat
        model_path = self.config.get("model") or self.config.get("model_folder")
        self.model = ModelContainer(self.samples, self.full_vocab)
        if model_path:
            if model_path.startswith("http"):
                model_path = ModelContainer.download_model(model_path)
            self.model.load_model(model_path)
        else:
            self.model.load_language(self.lang)

    def found_wake_word(self, frame_data):
        """ frame data contains audio data that needs to be checked for a wake
        word, you can process audio here or just return a result
        previously handled in update method """
        self._counter += self.SEC_BETWEEN_WW_CHECKS
        if self._counter < self.time_between_checks:
            return False
        self._counter = 0
        try:
            self.model.process_audio(frame_data, self.lang)
            transcript = self.model.get_final_transcription(self.lang)
        except:
            LOG.error("Failed to process audio")
            return False
        if not transcript or transcript == self.model.UNK:
            return False
        if self.debug:
            LOG.debug("TRANSCRIPT: " + transcript)
        return self.apply_rules(transcript, self.samples, self.rule, self.thresh)

    @classmethod
    def apply_rules(cls, transcript, samples, rule=MatchRule.FUZZY, thresh=0.75):
        for s in samples:
            s = s.lower().strip()
            if rule == MatchRule.FUZZY:
                score = fuzzy_match(s, transcript)
                if score >= thresh:
                    return True
            elif rule == MatchRule.TOKEN_SORT_RATIO:
                score = fuzzy_match(s, transcript,
                                    strategy=MatchStrategy.TOKEN_SORT_RATIO)
                if score >= thresh:
                    return True
            elif rule == MatchRule.TOKEN_SET_RATIO:
                score = fuzzy_match(s, transcript,
                                    strategy=MatchStrategy.TOKEN_SET_RATIO)
                if score >= thresh:
                    return True
            elif rule == MatchRule.PARTIAL_TOKEN_SORT_RATIO:
                score = fuzzy_match(s, transcript,
                                    strategy=MatchStrategy.PARTIAL_TOKEN_SORT_RATIO)
                if score >= thresh:
                    return True
            elif rule == MatchRule.PARTIAL_TOKEN_SET_RATIO:
                score = fuzzy_match(s, transcript,
                                    strategy=MatchStrategy.PARTIAL_TOKEN_SET_RATIO)
                if score >= thresh:
                    return True
            elif rule == MatchRule.CONTAINS:
                if s in transcript:
                    return True
            elif rule == MatchRule.EQUALS:
                if s == transcript:
                    return True
            elif rule == MatchRule.STARTS:
                if transcript.startswith(s):
                    return True
            elif rule == MatchRule.ENDS:
                if transcript.endswith(s):
                    return True
        return False


class MultiLangModelContainer(ModelContainer):
    engines = {}
    models = {}
    lang_samples = {}

    def __init__(self, lang_samples=None, full_vocab=False, default_lang="en"):
        if not full_vocab and not lang_samples:
            full_vocab = True
        lang = default_lang.split("-")[0].lower()
        self.lang_samples = lang_samples or {lang: [self.UNK]}
        samples = lang_samples[lang]
        self.default_lang = default_lang
        super().__init__(samples, full_vocab)

    def get_engine(self, lang=None):
        lang = lang or self.default_lang
        lang = lang.split("-")[0].lower()
        self.load_language(lang)
        return self.engines[lang]

    def load_model(self, model_path, lang=None):
        lang = lang or self.default_lang
        lang = lang.split("-")[0].lower()
        self.models[lang] = model_path
        samples = self.lang_samples.get(lang)
        self.engines[lang] = self.get_model(model_path, samples)

    def load_language(self, lang):
        lang = lang.split("-")[0].lower()
        if lang in self.engines:
            return
        model_path = self.download_language(lang)
        self.load_model(model_path, lang)

    def unload_language(self, lang):
        if lang in self.engines:
            del self.engines[lang]
            self.engines.pop(lang)


class VoskMultiWakeWordPlugin(HotWordEngine):
    """
     keeps multiple models in memory and runs detections for multiple wake words
     this avoids loading more than 1 model per language
     """
    # Hard coded values in mycroft/client/speech/mic.py
    SEC_BETWEEN_WW_CHECKS = 0.2
    MAX_EXPECTED_DURATION = 3  # seconds of data chunks received at a time

    def __init__(self, hotword="hey xxx", config=None, lang="en-us"):
        config = config or {}
        super().__init__(hotword, config, lang)
        self.keywords = self.config.get("keywords", {})
        self.expected_duration = self.MAX_EXPECTED_DURATION
        self.full_vocab = self.config.get("full_vocab", False)
        self.debug = self.config.get("debug", False)
        self.time_between_checks = min(self.config.get("time_between_checks", 1.0), 3)
        self._counter = 0
        self._load_model()
        # TODO refactor this, add native support to OPN
        self.bus = get_mycroft_bus()

    @property
    def langs(self):
        langs = [kw.get("lang", self.lang) for kw in self.keywords.values()]
        return list(set(langs))

    @property
    def samples(self):
        samples = {lang.split("-")[0].lower(): [] for lang in self.langs}
        for kw_name, kw in self.keywords.items():
            kw_name = kw_name.replace("_", " ").replace("-", " ")
            lang = kw.get("lang") or self.lang
            lang = lang.split("-")[0].lower()
            samples[lang] += kw.get("samples", [kw_name])
        return samples

    def _load_model(self):
        # keeps several models in memory per language
        self.model = MultiLangModelContainer(self.samples,
                                             self.full_vocab,
                                             self.lang)
        for lang in self.langs:
            self.model.load_language(lang)

    def found_wake_word(self, frame_data):
        """ frame data contains audio data that needs to be checked for a wake
        word, you can process audio here or just return a result
        previously handled in update method """
        self._counter += self.SEC_BETWEEN_WW_CHECKS
        if self._counter < self.time_between_checks:
            return False
        self._counter = 0
        txs = {}
        for kw_name, kw in self.keywords.items():
            lang = kw.get("lang") or self.lang
            if lang in txs:
                transcript = txs[lang]
            else:
                try:
                    self.model.process_audio(frame_data, lang)
                    transcript = self.model.get_final_transcription(lang)
                except:
                    LOG.error(f"Failed to process audio for lang: {lang}")
                    continue
            if not transcript or transcript == self.model.UNK:
                continue
            if self.debug:
                LOG.debug(f"TRANSCRIPT {lang}: " + transcript)
            samples = kw.get("samples") or [kw_name.replace("_", " ").replace("-", " ")]
            rule = kw.get("rule") or MatchRule.EQUALS
            thresh = kw.get("threshold", 0.75)
            wakeup = kw.get("wakeup", False)
            found = VoskWakeWordPlugin.apply_rules(transcript, samples, rule, thresh)
            if found:
                LOG.info(f"Detected kw: {kw_name}")
                if self.debug:
                    LOG.debug(str(kw))
                if wakeup:
                    self.bus.emit(Message('recognizer_loop:wake_up'))
                    return False
                return True
        return False
