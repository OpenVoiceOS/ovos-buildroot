# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from json_database import JsonStorageXDG
from ovos_plugin_manager.language import OVOSLangTranslationFactory
from ovos_utils.xdg_utils import xdg_cache_home
from quebra_frases import sentence_tokenize


class AbstractSolver:
    def __init__(self, name, priority=50, config=None):
        self.config = config or {}
        self.supported_langs = self.config.get("supported_langs") or []
        self.default_lang = self.config.get("lang", "en")
        if self.default_lang not in self.supported_langs:
            self.supported_langs.insert(0, self.default_lang)
        self.priority = priority
        self.translator = OVOSLangTranslationFactory.create()
        # cache contains raw data
        self.cache = JsonStorageXDG(name + "_data",
                                    xdg_folder=xdg_cache_home(),
                                    subfolder="neon_solvers")
        # spoken cache contains dialogs
        self.spoken_cache = JsonStorageXDG(name,
                                           xdg_folder=xdg_cache_home(),
                                           subfolder="neon_solvers")

    @staticmethod
    def sentence_split(text, max_sentences=25):
        return sentence_tokenize(text)[:max_sentences]

    def _get_user_lang(self, context, lang=None):
        context = context or {}
        lang = lang or context.get("lang") or self.default_lang
        lang = lang.split("-")[0]
        return lang

    def _tx_query(self, query, context=None, lang=None):
        context = context or {}
        lang = user_lang = self._get_user_lang(context, lang)

        # translate input to default lang
        if user_lang not in self.supported_langs:
            lang = self.default_lang
            query = self.translator.translate(query, lang, user_lang)

        context["lang"] = lang

        # HACK - cleanup some common translation mess ups
        # this is properly solving by using a good translate plugin
        # only common mistakes in default libretranslate plugin are handled
        query = query.replace("who is is ", "who is ")

        return query, context, lang

    # plugin methods to override
    def get_spoken_answer(self, query, context):
        """
        query assured to be in self.default_lang
        return a single sentence text response
        """
        return ""

    def get_data(self, query, context):
        """
        query assured to be in self.default_lang
        return a dict response
        """
        return {"short_answer": self.get_spoken_answer(query, context)}

    def get_image(self, query, context=None):
        """
        query assured to be in self.default_lang
        return path/url to a single image to acompany spoken_answer
        """
        return None

    def get_expanded_answer(self, query, context=None):
        """
        query assured to be in self.default_lang
        return a list of ordered steps to expand the answer, eg, "tell me more"

        {
            "title": "optional",
            "summary": "speak this",
            "img": "optional/path/or/url
        }
        :return:
        """
        return []

    def shutdown(self):
        """ module specific shutdown method """
        pass

    # user facing methods
    def search(self, query, context=None, lang=None):
        """
        cache and auto translate query if needed
        returns translated response from self.get_data
        """
        user_lang = self._get_user_lang(context, lang)
        query, context, lang = self._tx_query(query, context, lang)
        # read from cache
        if query in self.cache:
            data = self.cache[query]
        else:
            # search data
            try:
                data = self.get_data(query, context)
            except:
                return {}

        # save to cache
        self.cache[query] = data
        self.cache.store()

        # translate english output to user lang
        if user_lang not in self.supported_langs:
            return self.translator.translate_dict(data, user_lang, lang)
        return data

    def visual_answer(self, query, context=None, lang=None):
        """
        cache and auto translate query if needed
        returns image that answers query
        """
        query, context, lang = self._tx_query(query, context, lang)
        return self.get_image(query, context)

    def spoken_answer(self, query, context=None, lang=None):
        """
        cache and auto translate query if needed
        returns chunked and translated response from self.get_spoken_answer
        """
        user_lang = self._get_user_lang(context, lang)
        query, context, lang = self._tx_query(query, context, lang)

        # get answer
        if query in self.spoken_cache:
            # read from cache
            summary = self.spoken_cache[query]
        else:
            summary = self.get_spoken_answer(query, context)
            # save to cache
            self.spoken_cache[query] = summary
            self.spoken_cache.store()

        # summarize
        if summary:
            # translate english output to user lang
            if user_lang not in self.supported_langs:
                return self.translator.translate(summary, user_lang, lang)
            else:
                return summary

    def long_answer(self, query, context=None, lang=None):
        """
        return a list of ordered steps to expand the answer, eg, "tell me more"
        step0 is always self.spoken_answer and self.get_image
        {
            "title": "optional",
            "summary": "speak this",
            "img": "optional/path/or/url
        }
        :return:
        """
        user_lang = self._get_user_lang(context, lang)
        query, context, lang = self._tx_query(query, context, lang)
        steps = self.get_expanded_answer(query, context)

        # use spoken_answer as last resort
        if not steps:
            summary = self.get_spoken_answer(query, context)
            if summary:
                img = self.get_image(query, context)
                steps = [{"title": query, "summary": step0, "img": img}
                         for step0 in self.sentence_split(summary, -1)]

        # translate english output to user lang
        if user_lang not in self.supported_langs:
            return self.translator.translate_list(steps, user_lang, lang)
        return steps
