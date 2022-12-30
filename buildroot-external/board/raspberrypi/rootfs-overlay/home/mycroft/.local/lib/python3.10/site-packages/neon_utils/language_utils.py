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

from collections import namedtuple
from mycroft_bus_client import Message
from neon_utils.messagebus_utils import get_messagebus
try:
    from lingua_franca.internal import get_supported_langs
except ImportError:
    get_supported_langs = None


_bus = None
_default_lang = 'en'

SupportedLanguages = namedtuple('SupportedLanguages', ['stt', 'tts', 'skills'])


def _get_messagebus():
    global _bus
    if not _bus:
        _bus = get_messagebus()
    return _bus


def get_supported_languages(translation: bool = True) -> SupportedLanguages:
    """
    Get a dict of language support information.
    STT and TTS lists include languages that may not be supported by skills
    :param translation: Include skills languages supported via translation
    :returns: SupportedLanguages object with stt, tts, and skills language sets
    """
    return SupportedLanguages(stt=get_supported_input_langs(False),
                              tts=get_supported_output_langs(False),
                              skills=get_supported_skills_langs(translation))


def get_supported_skills_langs(translation: bool = True) -> set:
    """
    Get core language support for skills processing. This is the intersection
    of skills supported langs and Lingua Franca supported langs.
    :param translation: Include languages supported via translation
    :returns: set of languages supported in skills processing
    """
    lf_langs = set(get_supported_langs()) if get_supported_langs else set()
    msg = _get_messagebus().wait_for_response(Message("neon.languages.skills"))
    if not msg:
        langs = [_default_lang]
    elif translation:
        langs = msg.data.get('skill_langs')
    else:
        langs = msg.data.get('native_langs')
    langs = (lang.split('-')[0] for lang in langs)
    return lf_langs & set(langs) if lf_langs else set(langs)


def get_supported_input_langs(skill_support: bool = True,
                              translation: bool = True,
                              skills_langs: set = None) -> set:
    """
    Get the set of supported input languages
    :param skill_support: Only include languages also supported by skills
    :param translation: Include languages with skill support via translation
    :param skills_langs: Optional set of supported skills languages
    """
    msg = _get_messagebus().wait_for_response(Message("ovos.languages.stt"))
    stt_langs = set(lang.split('-')[0] for lang in msg.data.get('langs')) if \
        msg else set()
    if not skill_support:
        return stt_langs

    skills = skills_langs or get_supported_skills_langs(translation)
    return stt_langs & skills if stt_langs else {_default_lang}


def get_supported_output_langs(skill_support: bool = True,
                               translation: bool = True,
                               skills_langs: set = None) -> set:
    """
    Get the set of supported output languages
        :param skill_support: Only include languages also supported by skills
    :param translation: Include languages with skill support via translation
    :param skills_langs: Optional set of supported skills languages
    """
    msg = _get_messagebus().wait_for_response(Message("ovos.languages.tts"))
    tts_langs = set(lang.split('-')[0] for lang in msg.data.get('langs')) if \
        msg else set()
    if not skill_support:
        return tts_langs

    skills = skills_langs or get_supported_skills_langs(translation)
    return tts_langs & skills if tts_langs else {_default_lang}
