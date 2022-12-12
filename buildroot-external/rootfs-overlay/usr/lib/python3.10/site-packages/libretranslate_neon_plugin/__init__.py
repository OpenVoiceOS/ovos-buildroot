# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
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

import requests

from ovos_plugin_manager.templates.language import LanguageDetector,\
    LanguageTranslator

from libretranslate_neon_plugin.constants import DEFAULT_LIBRE_HOST


class LibreTranslateDetectPlugin(LanguageDetector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # host it yourself https://github.com/uav4geo/LibreTranslate
        self.url = self.config.get("libretranslate_host") or DEFAULT_LIBRE_HOST
        if not self.url.endswith("/detect"):
            self.url = f"{self.url}/detect"
        self.api_key = self.config.get("key")

    def detect(self, text):
        return self.detect_probs(text)[0]["language"]

    def detect_probs(self, text):
        params = {"q": text}
        if self.api_key:
            params["api_key"] = self.api_key
        result = requests.post(f"{self.url}", data=params)
        if not result.ok:
            raise Exception(result.text)
        return result.json()


class LibreTranslatePlugin(LanguageTranslator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # host it yourself https://github.com/uav4geo/LibreTranslate
        self.url = self.config.get("libretranslate_host") or DEFAULT_LIBRE_HOST
        if not self.url.endswith("/translate"):
            self.url = f"{self.url}/translate"
        self.api_key = self.config.get("key")

    def translate(self, text, target=None, source=None, url=None):
        source = source or self.default_language
        target = target or self.internal_language
        params = {"q": text,
                  "source": source.split("-")[0],
                  "target": target.split("-")[0]}
        if self.api_key:
            params["api_key"] = self.api_key
        r = requests.post(self.url, data=params)
        if not r.ok:
            raise Exception(r.text)
        if r.json().get("error"):
            return None
        return r.json()["translatedText"].strip().rstrip('.')
