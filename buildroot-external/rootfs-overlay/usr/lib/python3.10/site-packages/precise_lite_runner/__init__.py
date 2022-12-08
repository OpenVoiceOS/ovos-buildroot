import numpy as np

from precise_lite_runner.runner import ReadWriteStream, \
    PreciseRunner, TFLiteRunner, Listener
from precise_lite_runner.util import buffer_to_audio, ThresholdDecoder
from precise_lite_runner.vectorization import vectorize_raw, add_deltas
from precise_lite_runner.params import params


class PreciseLiteListener:
    def __init__(self, model, chunk_size, trigger_level, sensitivity,
                 on_activation=None, on_prediction=None, stream=None):
        on_activation = on_activation or self.on_activation
        on_prediction = on_prediction or self.on_prediction
        self.listener = Listener(model, chunk_size)
        self.audio_buffer = np.zeros(params.buffer_samples,
                                     dtype=float)
        self.listener.get_prediction = self.get_prediction
        self.runner = PreciseRunner(self.listener, trigger_level,
                                    stream=stream,
                                    sensitivity=sensitivity,
                                    on_activation=on_activation,
                                    on_prediction=on_prediction)

    def on_activation(self):
        print("     precise-lite activation!!!")

    def on_prediction(self, conf):
        pass

    def get_prediction(self, chunk):
        audio = buffer_to_audio(chunk)
        self.audio_buffer = np.concatenate(
            (self.audio_buffer[len(audio):], audio))
        return self.listener.update(audio)

    def start(self):
        self.runner.start()

    def stop(self):
        self.runner.stop()

