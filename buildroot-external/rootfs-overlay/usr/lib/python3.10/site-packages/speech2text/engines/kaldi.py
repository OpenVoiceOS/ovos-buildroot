from speech2text.engines import STT, StreamThread, StreamingSTT
import re
from os.path import isdir
import json
import requests
from speech2text.log import LOG
from queue import Queue


class KaldiServerSTT(STT):
    """ https://github.com/alumae/kaldi-gstreamer-server """
    def execute(self, audio, language=None):
        response = requests.post(self.config.get("uri"),
                                 data=audio.get_wav_data())
        try:
            hypotheses = response.json()["hypotheses"]
            return re.sub(r'\s*\[noise\]\s*', '', hypotheses[0]["utterance"])
        except Exception:
            return None


class VoskKaldiSTT(STT):
    def __init__(self, config=None):
        super().__init__(config)
        global KaldiRecognizer
        from vosk import Model as KaldiModel, KaldiRecognizer
        model_path = self.config.get("model")
        if not model_path or not isdir(model_path):
            LOG.error("You need to provide a valid model file")
            LOG.info("download a model from https://github.com/alphacep/vosk-api/blob/master/doc/models.md")
            raise FileNotFoundError
        self.model = KaldiModel(model_path)

    def execute(self, audio, language=None):
        kaldi = KaldiRecognizer(self.model, 16000)
        kaldi.AcceptWaveform(audio.get_wav_data())
        res = kaldi.FinalResult()
        res = json.loads(res)
        return res["text"]


class VoskKaldiStreamThread(StreamThread):
    def __init__(self, queue, lang, kaldi):
        super().__init__(queue, lang)
        self.kaldi = kaldi

    def handle_audio_stream(self, audio, language):
        for a in audio:
            data = np.frombuffer(a, np.int16)
            if self.kaldi.AcceptWaveform(data):
                res = self.kaldi.Result()
                res = json.loads(res)
                self.text = res["text"]
            else:
                res = self.kaldi.PartialResult()
                res = json.loads(res)
                self.text = res["partial"]

        return self.text


class VoskKaldiStreamingSTT(StreamingSTT, VoskKaldiSTT):

    def __init__(self, config=None):
        super().__init__(config)
        global np
        import numpy as np

    def create_streaming_thread(self):
        self.queue = Queue()
        kaldi = KaldiRecognizer(self.model, 16000)
        return VoskKaldiStreamThread(
            self.queue,
            self.lang,
            kaldi
        )
