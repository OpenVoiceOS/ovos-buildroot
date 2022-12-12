from speech2text.engines import KeySTT


class HoundifySTT(KeySTT):
    def execute(self, audio, language=None):
        self.lang = language or self.lang
        return self.recognizer.recognize_houndify(audio, self.id, self.key)

