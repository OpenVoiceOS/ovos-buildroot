from ovos_plugin_manager.templates.vad import VADEngine
import webrtcvad


class WebRTCVAD(VADEngine):
    def __init__(self, config=None, sample_rate=None):
        super().__init__(config, sample_rate)
        self.vad_mode = self.config.get("vad_mode", 3)
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(self.vad_mode)

    def is_silence(self, chunk):
        # return True or False
        return not self.vad.is_speech(chunk, self.sample_rate)


