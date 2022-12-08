from speech2text.engines import BasicSTT


class IBMSTT(BasicSTT):
    def execute(self, audio, language=None):
        self.lang = language or self.lang
        return self.recognizer.recognize_ibm(audio, self.username,
                                             self.password, self.lang)
