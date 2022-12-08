from speech2text.log import LOG
from speech2text.engines.kaldi import KaldiServerSTT, VoskKaldiSTT, VoskKaldiStreamingSTT
from speech2text.engines.bing import BingSTT
from speech2text.engines.ds import DeepSpeechServerSTT, \
    DeepSpeechStreamServerSTT, DeepSpeechSTT, DeepSpeechStreamSTT
from speech2text.engines.govivace import GoVivaceSTT
from speech2text.engines.google import GoogleCloudStreamingSTT, \
    GoogleCloudSTT, GoogleSTT
from speech2text.engines.houndify import HoundifySTT
from speech2text.engines.yandex import YandexSTT
from speech2text.engines.ibm import IBMSTT
from speech2text.engines.wit import WITSTT


class STTFactory:
    CLASSES = {
        "google": GoogleSTT,
        "google_cloud": GoogleCloudSTT,
        "google_cloud_streaming": GoogleCloudStreamingSTT,
        "wit": WITSTT,
        "ibm": IBMSTT,
        "kaldi_server": KaldiServerSTT,
        "kaldi": KaldiServerSTT, # TODO remove in next release, backwards compat
        "kaldi_vosk": VoskKaldiSTT,
        "kaldi_vosk_streaming": VoskKaldiStreamingSTT,
        "bing": BingSTT,
        "govivace": GoVivaceSTT,
        "houndify": HoundifySTT,
        "deepspeech_server": DeepSpeechServerSTT,
        "deepspeech_stream_server": DeepSpeechStreamServerSTT,
        "deepspeech": DeepSpeechSTT,
        "deepspeech_streaming": DeepSpeechStreamSTT,
        "yandex": YandexSTT
    }

    @staticmethod
    def create(config=None, engines=None):
        engines = engines or STTFactory.CLASSES
        config = config or {"module": "google"}
        module = config["module"]
        module_config = config.get(module, config)
        clazz = engines.get(module)
        return clazz(module_config)
