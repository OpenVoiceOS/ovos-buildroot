class KeywordExtractor:
    def __init__(self, config=None):
        self.config = config or {}

    def extract(self, text, lang):
        return {text: 0.0}
