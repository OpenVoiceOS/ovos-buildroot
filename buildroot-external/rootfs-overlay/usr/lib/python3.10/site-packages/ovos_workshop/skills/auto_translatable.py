from ovos_utils import get_handler_name
from ovos_utils.log import LOG
from ovos_utils.lang.translate import detect_lang, translate_text
from ovos_workshop.skills.ovos import OVOSSkill, OVOSFallbackSkill


class UniversalSkill(OVOSSkill):
    ''' Skill that auto translates input/output from any language '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_lang = self.lang
        self.translate_keys = []
        self.translate_tags = True

    def detect_language(self, utterance):
        try:
            return detect_lang(utterance)
        except:
            return self.lang.split("-")[0]

    def translate(self, text, lang=None):
        lang = lang or self.lang
        translated = translate_text(text, lang)
        LOG.info("translated " + text + " to " + translated)
        return translated

    def _translate_utterance(self, utterance="", lang=None):
        lang = lang or self.input_lang
        if utterance and lang is not None:
            ut_lang = self.detect_language(utterance)
            if lang.split("-")[0] != ut_lang:
                utterance = self.translate(utterance, lang)
        return utterance

    def _translate_message(self, message):
        ut = message.data.get("utterance")
        if ut:
            message.data["utterance"] = self._translate_utterance(ut)
        for key in self.translate_keys:
            if key in message.data:
                ut = message.data[key]
                message.data[key] = self._translate_utterance(ut)
        if self.translate_tags:
            for idx, token in enumerate(message.data["__tags__"]):
                message.data["__tags__"][idx] = self._translate_utterance(token.get("key", ""))
        return message

    def create_universal_handler(self, handler):

        def universal_intent_handler(message):
            message = self._translate_message(message)
            LOG.info(get_handler_name(handler))
            handler(message)

        return universal_intent_handler

    def register_intent(self, intent_parser, handler):
        handler = self.create_universal_handler(handler)
        super().register_intent(intent_parser, handler)

    def register_intent_file(self, intent_file, handler):
        handler = self.create_universal_handler(handler)
        super().register_intent_file(intent_file, handler)

    def speak(self, utterance, expect_response=False, wait=False):
        utterance = self._translate_utterance(utterance)
        super().speak(utterance, expect_response, wait)


class UniversalFallback(UniversalSkill, OVOSFallbackSkill):
    ''' Fallback Skill that auto translates input/output from any language '''

    def create_universal_fallback_handler(self, handler):

        def universal_fallback_handler(message):
            # auto_Translate input
            message = self._translate_message(message)
            LOG.info(get_handler_name(handler))
            success = handler(self, message)
            if success:
                self.make_active()
            return success

        return universal_fallback_handler

    def register_fallback(self, handler, priority):
        handler = self.create_universal_fallback_handler(handler)
        self.instance_fallback_handlers.append(handler)
        self._register_fallback(handler, priority)
