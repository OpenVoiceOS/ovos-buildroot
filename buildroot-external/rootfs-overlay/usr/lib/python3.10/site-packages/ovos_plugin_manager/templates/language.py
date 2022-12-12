from ovos_config.config import Configuration


class LanguageDetector:
    def __init__(self, config=None):
        self.config = config or {}
        self.default_language = self.config.get("lang") or "en-us"
        # hint_language: str  E.g., 'it' boosts Italian
        self.hint_language = self.config.get("hint_lang") or \
            self.config.get('user') or self.default_language
        # boost score for this language
        self.boost = self.config.get("boost")

    def detect(self, text):
        # assume default language
        return self.default_language

    def detect_probs(self, text):
        return {self.detect(text): 1}

    @property
    def available_languages(self) -> set:
        """
        Return languages supported by this detector implementation in this state.
        This should be a set of languages this detector is capable of recognizing.
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set()


class LanguageTranslator:
    def __init__(self, config=None):
        self.config = config or {}
        # translate from, unless specified/detected otherwise
        self.default_language = self.config.get("lang") or "en-us"
        # translate to
        self.internal_language = (Configuration().get('language') or
                                  dict()).get("internal") or \
            self.default_language

    def translate(self, text, target=None, source=None):
        return text

    def translate_dict(self, data, lang_tgt, lang_src="en"):
        for k, v in data.items():
            if isinstance(v, dict):
                data[k] = self.translate_dict(v, lang_tgt, lang_src)
            elif isinstance(v, str):
                data[k] = self.translate(v, lang_tgt, lang_src)
            elif isinstance(v, list):
                data[k] = self.translate_list(v, lang_tgt, lang_src)
        return data

    def translate_list(self, data, lang_tgt, lang_src="en"):
        for idx, v in enumerate(data):
            if isinstance(v, dict):
                data[idx] = self.translate_dict(v, lang_tgt, lang_src)
            elif isinstance(v, str):
                data[idx] = self.translate(v, lang_tgt, lang_src)
            elif isinstance(v, list):
                data[idx] = self.translate_list(v, lang_tgt, lang_src)
        return data

    @property
    def available_languages(self) -> set:
        """
        Return languages supported by this translator implementation in this state.
        Any language in this set should be translatable to any other language in the set.
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set()

    def supported_translations(self, source_lang: str = None) -> set:
        """
        Return valid target languages we can translate `source_lang` to.
        This method should be overridden by the derived class.
        Args:
            source_lang: ISO 639-1 source language code
        Returns:
            set of ISO 639-1 languages the source language can be translated to
        """
        return self.available_languages
