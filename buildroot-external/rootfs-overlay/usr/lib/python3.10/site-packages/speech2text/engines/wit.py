from speech2text.engines import TokenSTT
from speech2text.log import LOG


class WITSTT(TokenSTT):
    def execute(self, audio, language=None):
        LOG.warning("WITSTT language should be configured at wit.ai settings.")
        return self.recognizer.recognize_wit(audio, self.token)

