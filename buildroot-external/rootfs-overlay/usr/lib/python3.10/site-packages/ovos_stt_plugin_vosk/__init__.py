import json
from time import sleep
from os.path import join, exists
from ovos_plugin_manager.templates.stt import STT, StreamThread, StreamingSTT
from ovos_skill_installer import download_extract_zip, download_extract_tar
from ovos_utils.log import LOG
from ovos_utils.network_utils import is_connected
from ovos_utils.xdg_utils import xdg_data_home
from queue import Queue
from speech_recognition import AudioData
from vosk import Model as KaldiModel, KaldiRecognizer

_lang2url = {
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
_biglang2url = {
    "en": "https://alphacephei.com/vosk/models/vosk-model-en-us-aspire-0.2.zip",
    "en-in": "http://alphacephei.com/vosk/models/vosk-model-en-in-0.4.zip",
    "cn": "https://alphacephei.com/vosk/models/vosk-model-cn-0.1.zip",
    "ru": "https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip",
    "fr": "https://github.com/pguyot/zamia-speech/releases/download/20190930/kaldi-generic-fr-tdnn_f-r20191016.tar.xz",
    "de": "https://alphacephei.com/vosk/models/vosk-model-de-0.6.zip",
    "nl": "https://alphacephei.com/vosk/models/vosk-model-nl-spraakherkenning-0.6.zip",
    "fa": "https://alphacephei.com/vosk/models/vosk-model-fa-0.5.zip"

}

VoskSTTConfig = {
    lang: [{"model": url,
            "lang": lang,
            "meta": {
                "priority": 40,
                "display_name": url.split("/")[-1].replace(".zip", "") + " (Small)",
                "offline": True}
            }]
    for lang, url in _lang2url.items()
}
for lang, url in _biglang2url.items():
    VoskSTTConfig[lang].append({"model": url,
                                "lang": lang,
                                "meta": {
                                    "priority": 70,
                                    "display_name": url.split("/")[-1].replace(".zip", "") + " (Large)",
                                    "offline": True}
                                })


class ModelContainer:
    def __init__(self):
        self.engines = {}
        self.models = {}

    def get_engine(self, lang):
        lang = lang.split("-")[0].lower()
        self.load_language(lang)
        return self.engines[lang]

    def get_partial_transcription(self, lang):
        engine = self.get_engine(lang)
        res = engine.PartialResult()
        return json.loads(res)["partial"]

    def get_final_transcription(self, lang):
        engine = self.get_engine(lang)
        res = engine.FinalResult()
        return json.loads(res)["text"]

    def process_audio(self, audio, lang):
        engine = self.get_engine(lang)
        if isinstance(audio, AudioData):
            audio = audio.get_wav_data()
        return engine.AcceptWaveform(audio)

    def enable_limited_vocabulary(self, words, lang):
        """
        enable limited vocabulary mode
        will only consider pre defined .voc files
        """
        model_path = self.models[lang]
        self.engines[lang] = KaldiRecognizer(
            KaldiModel(model_path), 16000, json.dumps(words))

    def enable_full_vocabulary(self, lang=None):
        """ enable default transcription mode """
        model_path = self.models[lang]
        self.engines[lang] = KaldiRecognizer(
            KaldiModel(model_path), 16000)

    def load_model(self, model_path, lang):
        lang = lang.split("-")[0].lower()
        self.models[lang] = model_path
        if model_path:
            self.engines[lang] = KaldiRecognizer(KaldiModel(model_path), 16000)
        else:
            raise FileNotFoundError

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
        name = url.split("/")[-1].rsplit(".", 1)[0]
        model_path = join(folder, name)
        if not exists(model_path):
            while not is_connected():
                LOG.info("Waiting for internet in order to download vosk language model")
                # waiting for wifi setup most likely
                sleep(10)
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
        if not small:
            _lang2url.update(_biglang2url)
        lang = lang.lower()
        if lang in _lang2url:
            return _lang2url[lang]
        lang = lang.split("-")[0]
        return _lang2url.get(lang)


class VoskKaldiSTT(STT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # model_folder for backwards compat
        model_path = self.config.get("model_folder") or self.config.get("model")

        self.model = ModelContainer()
        if model_path:
            if model_path.startswith("http"):
                model_path = ModelContainer.download_model(model_path)
            self.model.load_model(model_path, self.lang)
        else:
            self.model.load_language(self.lang)
        self.verbose = True

    def load_language(self, lang):
        self.model.load_language(lang)

    def unload_language(self, lang):
        self.model.unload_language(lang)

    def enable_limited_vocabulary(self, words, lang):
        self.model.enable_limited_vocabulary(words, lang or self.lang)

    def enable_full_vocabulary(self, lang=None):
        self.model.enable_full_vocabulary(lang or self.lang)

    def execute(self, audio, language=None):
        lang = language or self.lang
        self.model.process_audio(audio, lang)
        return self.model.get_final_transcription(lang)


class VoskKaldiStreamThread(StreamThread):
    def __init__(self, queue, lang, model, verbose=True):
        super().__init__(queue, lang)
        self.model = model
        self.verbose = verbose
        self.previous_partial = ""
        self.running = True

    def handle_audio_stream(self, audio, language):
        lang = language or self.language
        if self.running:
            for a in audio:
                self.model.process_audio(a, lang)
                self.text = self.model.get_partial_transcription(lang)
                if self.verbose:
                    if self.previous_partial != self.text:
                        LOG.info("Partial Transcription: " + self.text)
                self.previous_partial = self.text
        return self.text

    def finalize(self):
        self.running = False
        if self.previous_partial:
            if self.verbose:
                LOG.info("Finalizing stream")
            self.text = self.model.get_final_transcription(self.language)
            self.previous_partial = ""
        text = str(self.text)
        self.text = ""
        return text


class VoskKaldiStreamingSTT(StreamingSTT, VoskKaldiSTT):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose = self.config.get("verbose", False)

    def create_streaming_thread(self):
        self.queue = Queue()
        return VoskKaldiStreamThread(
            self.queue, self.lang, self.model, self.verbose
        )
