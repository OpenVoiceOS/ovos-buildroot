from speech2text.engines import TokenSTT


class BingSTT(TokenSTT):
    def execute(self, audio, language=None):
        self.lang = language or self.lang
        return self.recognizer.recognize_bing(audio, self.token,
                                              self.lang)
