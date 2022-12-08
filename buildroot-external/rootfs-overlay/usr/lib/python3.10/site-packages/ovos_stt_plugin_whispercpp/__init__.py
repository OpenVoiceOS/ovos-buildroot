import ctypes
import os
import pathlib

# this is needed to read the WAV file properly
import numpy
import requests
from ovos_plugin_manager.templates.stt import STT
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_data_home
from speech_recognition import AudioData


# this needs to match the C struct in whisper.h
class WhisperFullParams(ctypes.Structure):
    _fields_ = [
        ("strategy", ctypes.c_int),
        ("n_threads", ctypes.c_int),
        ("offset_ms", ctypes.c_int),
        ("translate", ctypes.c_bool),
        ("no_context", ctypes.c_bool),
        ("print_special_tokens", ctypes.c_bool),
        ("print_progress", ctypes.c_bool),
        ("print_realtime", ctypes.c_bool),
        ("print_timestamps", ctypes.c_bool),
        ("language", ctypes.c_char_p),
        ("greedy", ctypes.c_int * 1),
    ]


class WhisperEngine:
    def __init__(self, libname, model_path):
        # load library and model
        self.libname = pathlib.Path().absolute() / libname
        self.whisper = ctypes.CDLL(libname)

        # tell Python what are the return types of the functions
        self.whisper.whisper_init.restype = ctypes.c_void_p
        self.whisper.whisper_full_default_params.restype = WhisperFullParams
        self.whisper.whisper_full_get_segment_text.restype = ctypes.c_char_p

        # initialize whisper.cpp context
        self.ctx = self.whisper.whisper_init(model_path.encode("utf-8"))

        # get default whisper parameters and adjust as needed
        self.params = self.whisper.whisper_full_default_params(0)
        self.params.print_realtime = False
        self.params.print_progress = False
        self.params.print_timestamps = False
        self.params.n_threads = os.cpu_count() - 1
        self.params.translate = False

    def audiodata2array(self, audio_data):
        assert isinstance(audio_data, AudioData)
        # Convert buffer to float32 using NumPy
        audio_as_np_int16 = numpy.frombuffer(audio_data.get_wav_data(), dtype=numpy.int16)
        audio_as_np_float32 = audio_as_np_int16.astype(numpy.float32)

        # Normalise float32 array so that values are between -1.0 and +1.0
        max_int16 = 2 ** 15
        data = audio_as_np_float32 / max_int16
        return data

    def transcribe_wav(self, wav, lang="en"):
        with AudioFile(wav) as source:
            audio = Recognizer().record(source)
        return self.transcribe_audio(audio, lang)

    def transcribe_audio(self, audio, lang="en"):
        lang = lang.lower().split("-")[0]
        self.params.language = lang.encode()

        data = self.audiodata2array(audio)

        # run the inference
        result = self.whisper.whisper_full(ctypes.c_void_p(self.ctx), self.params,
                                           data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                           len(data))
        if result != 0:
            raise RuntimeError(f"Error: {result}")

        # print results from Python
        n_segments = self.whisper.whisper_full_n_segments(ctypes.c_void_p(self.ctx))
        txt = b""
        for i in range(n_segments):
            txt += self.whisper.whisper_full_get_segment_text(ctypes.c_void_p(self.ctx), i)
        return txt.decode("utf-8").strip()

    def shutdown(self):
        # free the memory
        self.whisper.whisper_free(ctypes.c_void_p(self.ctx))


class WhispercppSTT(STT):
    DOWNLOAD_URL = "https://ggml.ggerganov.com/ggml-model-whisper-{model}.bin"
    MODELS = ("tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large")
    LANGUAGES = {
        "en": "english",
        "zh": "chinese",
        "de": "german",
        "es": "spanish",
        "ru": "russian",
        "ko": "korean",
        "fr": "french",
        "ja": "japanese",
        "pt": "portuguese",
        "tr": "turkish",
        "pl": "polish",
        "ca": "catalan",
        "nl": "dutch",
        "ar": "arabic",
        "sv": "swedish",
        "it": "italian",
        "id": "indonesian",
        "hi": "hindi",
        "fi": "finnish",
        "vi": "vietnamese",
        "iw": "hebrew",
        "uk": "ukrainian",
        "el": "greek",
        "ms": "malay",
        "cs": "czech",
        "ro": "romanian",
        "da": "danish",
        "hu": "hungarian",
        "ta": "tamil",
        "no": "norwegian",
        "th": "thai",
        "ur": "urdu",
        "hr": "croatian",
        "bg": "bulgarian",
        "lt": "lithuanian",
        "la": "latin",
        "mi": "maori",
        "ml": "malayalam",
        "cy": "welsh",
        "sk": "slovak",
        "te": "telugu",
        "fa": "persian",
        "lv": "latvian",
        "bn": "bengali",
        "sr": "serbian",
        "az": "azerbaijani",
        "sl": "slovenian",
        "kn": "kannada",
        "et": "estonian",
        "mk": "macedonian",
        "br": "breton",
        "eu": "basque",
        "is": "icelandic",
        "hy": "armenian",
        "ne": "nepali",
        "mn": "mongolian",
        "bs": "bosnian",
        "kk": "kazakh",
        "sq": "albanian",
        "sw": "swahili",
        "gl": "galician",
        "mr": "marathi",
        "pa": "punjabi",
        "si": "sinhala",
        "km": "khmer",
        "sn": "shona",
        "yo": "yoruba",
        "so": "somali",
        "af": "afrikaans",
        "oc": "occitan",
        "ka": "georgian",
        "be": "belarusian",
        "tg": "tajik",
        "sd": "sindhi",
        "gu": "gujarati",
        "am": "amharic",
        "yi": "yiddish",
        "lo": "lao",
        "uz": "uzbek",
        "fo": "faroese",
        "ht": "haitian creole",
        "ps": "pashto",
        "tk": "turkmen",
        "nn": "nynorsk",
        "mt": "maltese",
        "sa": "sanskrit",
        "lb": "luxembourgish",
        "my": "myanmar",
        "bo": "tibetan",
        "tl": "tagalog",
        "mg": "malagasy",
        "as": "assamese",
        "tt": "tatar",
        "haw": "hawaiian",
        "ln": "lingala",
        "ha": "hausa",
        "ba": "bashkir",
        "jw": "javanese",
        "su": "sundanese",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lib = self.config.get("lib") or "~/.local/bin/libwhisper.so"
        self.lib = os.path.expanduser(lib)
        # self.bin = os.path.expanduser("~/whisper.cpp/main")
        if not os.path.isfile(self.lib):
            LOG.error("you need to provicde libwhisper.so, please follow the README.md instructions")
            raise ImportError("libwhisper.so not found")

        self.model_folder = self.config.get("model_folder") or f"{xdg_data_home()}/whispercpp"
        model = self.config.get("model")
        if not model:
            model = "tiny"
        os.makedirs(self.model_folder, exist_ok=True)
        model_path = self.get_model(model)
        self.engine = WhisperEngine(self.lib, model_path)

    def get_model(self, model_name):
        if os.path.isfile(model_name):
            return model_name
        if model_name not in self.MODELS:
            raise ValueError(f"unknown model for Whisper: {model_name}")
        model_path = f"{self.model_folder}/{model_name}"
        if not os.path.isfile(model_path):
            url = self.DOWNLOAD_URL.format(model=model_name)
            LOG.info(f"Downloading {url}")
            data = requests.get(url).content
            with open(model_path, "wb") as f:
                f.write(data)
        return model_path

    def execute(self, audio, language=None):
        lang = language or self.lang
        return self.engine.transcribe_audio(audio, lang)

    @property
    def available_languages(self) -> set:
        return set(self.LANGUAGES.keys())

    def __del__(self):
        if self.engine:
            self.engine.shutdown()


WhispercppSTTConfig = {
    lang: [{"model": "tiny",
            "lang": lang,
            "meta": {
                "priority": 50,
                "display_name": f"WhisperCPP (Tiny)",
                "offline": True}
            },
           {"model": "base",
            "lang": lang,
            "meta": {
                "priority": 55,
                "display_name": f"WhisperCPP (Base)",
                "offline": True}
            },
           {"model": "small",
            "lang": lang,
            "meta": {
                "priority": 60,
                "display_name": f"WhisperCPP (Small)",
                "offline": True}
            }
           ]
    for lang, lang_name in WhispercppSTT.LANGUAGES.items()
}

if __name__ == "__main__":
    b = WhispercppSTT()
    from speech_recognition import Recognizer, AudioFile

    jfk = "/home/user/whisper.cpp/samples/jfk.wav"
    with AudioFile(jfk) as source:
        audio = Recognizer().record(source)

    a = b.execute(audio, language="en")
    print(a)

