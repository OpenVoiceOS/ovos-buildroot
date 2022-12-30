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

import os
import sys
import unittest

from ovos_utils.messagebus import FakeBus

import neon_utils.language_utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class LanguageUtilTests(unittest.TestCase):
    bus = FakeBus()

    @classmethod
    def setUpClass(cls) -> None:
        import neon_utils.language_utils
        neon_utils.language_utils._bus = cls.bus

    def test_get_supported_skills_langs(self):
        from neon_utils.language_utils import get_supported_skills_langs, \
            _default_lang

        skill_langs = ['en', 'es', 'fr']
        native_langs = ['en']
        translate_langs = ['en', 'es', 'fr']

        def _skill_langs(msg):
            self.bus.emit(msg.response({"skill_langs": skill_langs,
                                        "native_langs": native_langs,
                                        "translate_langs": translate_langs}))

        # Test default no API response
        self.assertEqual(get_supported_skills_langs(), {_default_lang})

        # Test no translation
        self.bus.once('neon.languages.skills', _skill_langs)
        self.assertEqual(get_supported_skills_langs(False), {'en'})

        # Test with translation
        self.bus.once('neon.languages.skills', _skill_langs)
        self.assertEqual(get_supported_skills_langs(True), {'en', 'es', 'fr'})

        # Test LF unsupported lang
        translate_langs.append('na')
        skill_langs.append('na')
        self.bus.once('neon.languages.skills', _skill_langs)
        self.assertEqual(get_supported_skills_langs(True), {'en', 'es', 'fr'})

    def test_get_supported_input_langs(self):
        from neon_utils.language_utils import get_supported_input_langs, \
            _default_lang

        stt_langs = ['en', 'uk-ua']

        def _stt_langs(msg):
            self.bus.emit(msg.response({"langs": stt_langs}))

        # Test default no API response
        self.assertEqual(get_supported_input_langs(skills_langs=set()),
                         {_default_lang})

        # Test skill supported languages
        self.bus.once('ovos.languages.stt', _stt_langs)
        self.assertEqual(get_supported_input_langs(skill_support=True,
                                                   skills_langs={'en', 'uk'}),
                         {'en', 'uk'})

        # Test skill unsupported languages
        self.bus.once('ovos.languages.stt', _stt_langs)
        self.assertEqual(get_supported_input_langs(skill_support=True,
                                                   skills_langs={'en', 'es'}),
                         {'en'})

        # Test skill unsupported languages
        self.bus.once('ovos.languages.stt', _stt_langs)
        self.assertEqual(get_supported_input_langs(skill_support=False,
                                                   skills_langs={'en', 'es'}),
                         {'en', 'uk'})

    def test_get_supported_output_langs(self):
        from neon_utils.language_utils import get_supported_output_langs, \
            _default_lang

        tts_langs = ['en-us', 'en-uk', 'uk-ua']

        def _tts_langs(msg):
            self.bus.emit(msg.response({"langs": tts_langs}))

        # Test default no API response
        self.assertEqual(get_supported_output_langs(skills_langs=set()),
                         {_default_lang})

        # Test skill supported languages
        self.bus.once('ovos.languages.tts', _tts_langs)
        self.assertEqual(get_supported_output_langs(skill_support=True,
                                                    skills_langs={'en', 'uk'}),
                         {'en', 'uk'})

        # Test skill unsupported languages
        self.bus.once('ovos.languages.tts', _tts_langs)
        self.assertEqual(get_supported_output_langs(skill_support=True,
                                                    skills_langs={'en', 'es'}),
                         {'en'})

        # Test skill unsupported languages
        self.bus.once('ovos.languages.tts', _tts_langs)
        self.assertEqual(get_supported_output_langs(skill_support=False,
                                                    skills_langs={'en', 'es'}),
                         {'en', 'uk'})

    def test_get_supported_languages(self):
        from neon_utils.language_utils import get_supported_languages,\
            SupportedLanguages
        tts_langs = ['en-us', 'uk-ua', 'es-mx']
        stt_langs = ['en-us', 'es-es', 'pt-pt']
        native_langs = ['en', 'na']
        translate_langs = ['en', 'es', 'fr']

        def _stt_langs(msg):
            self.bus.emit(msg.response({'langs': stt_langs}))

        def _tts_langs(msg):
            self.bus.emit(msg.response({'langs': tts_langs}))

        def _skill_langs(msg):
            self.bus.emit(msg.response({
                'native_langs': native_langs,
                'translate_langs': translate_langs,
                'skill_langs': list(set(native_langs + translate_langs))}))

        self.bus.once('ovos.languages.tts', _tts_langs)
        self.bus.once('ovos.languages.stt', _stt_langs)
        self.bus.once('neon.languages.skills', _skill_langs)
        no_translate_langs = get_supported_languages(False)
        self.assertIsInstance(no_translate_langs, SupportedLanguages)
        self.assertEqual(no_translate_langs.tts, {'en', 'uk', 'es'})
        self.assertEqual(no_translate_langs.stt, {'en', 'es', 'pt'})
        self.assertEqual(no_translate_langs.skills, {'en'})

        self.bus.once('ovos.languages.tts', _tts_langs)
        self.bus.once('ovos.languages.stt', _stt_langs)
        self.bus.once('neon.languages.skills', _skill_langs)
        with_translate_langs = get_supported_languages(True)
        self.assertIsInstance(with_translate_langs, SupportedLanguages)
        self.assertEqual(with_translate_langs.tts, {'en', 'uk', 'es'})
        self.assertEqual(with_translate_langs.stt, {'en', 'es', 'pt'})
        self.assertEqual(with_translate_langs.skills, {'en', 'es', 'fr'})


if __name__ == '__main__':
    unittest.main()
