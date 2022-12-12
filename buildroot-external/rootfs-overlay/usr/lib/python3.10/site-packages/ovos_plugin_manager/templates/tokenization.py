from mycroft_bus_client.message import dig_for_message
from quebra_frases import span_indexed_word_tokenize, word_tokenize


class Tokenizer:
    def __init__(self, config=None):
        self.config = config or {}

    @property
    def lang(self):
        lang = self.config.get("lang")
        msg = dig_for_message()
        if msg:
            lang = msg.data.get("lang")
        return lang or "en-us"

    def span_tokenize(self, text, lang=None):
        lang = lang or self.lang
        return span_indexed_word_tokenize(text)

    def tokenize(self, text, lang=None):
        lang = lang or self.lang
        return word_tokenize(text)

    @staticmethod
    def restore_spans(spans):
        # restore sentence from spans
        sentence = ""
        for start, end, token in spans:
            if start > len(sentence):
                sentence += " "
            sentence += token
        return sentence
