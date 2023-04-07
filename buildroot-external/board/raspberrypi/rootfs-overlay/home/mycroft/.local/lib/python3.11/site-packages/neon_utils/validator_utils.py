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

from neon_utils import LOG
from lingua_franca import parse, set_default_lang

from mycroft.skills.core import MycroftSkill


def numeric_confirmation_validator(confirmation_num: str, lang: str = "en"):
    """
    Returns a validator method that returns true if the confirmation_num is in the passed string.
     The confirmation_num must be the only number in the utterance (something 123 != 1 something 123).
    :param confirmation_num: number to locate in utterance
    :param lang: language to use for extracting number from strings
    :return: True if the confirmation is in the spoken utterance.
    """
    if not isinstance(confirmation_num, str):
        raise TypeError(f"Expected str, got {type(confirmation_num)}")
    if not confirmation_num.isnumeric():
        raise ValueError(f"{confirmation_num} is not numeric")

    set_default_lang(lang)

    def wrapped_validator(utt):
        spoken_num = "".join([str(round(n)) for n in parse.extract_numbers(utt)])
        return confirmation_num == spoken_num
    return wrapped_validator


def string_confirmation_validator(confirmation_str: str):
    """
    Returns a validator method that returns true if the confirmation_str is in the passed string.
    :param confirmation_str: substring to locate in utterance
    :return: True if the confirmation is in the spoken utterance.
    """
    if not isinstance(confirmation_str, str):
        raise TypeError(f"Expected str, got {type(confirmation_str)}")
    if not confirmation_str:
        raise ValueError(f"Got empty confirmation string")

    def wrapped_validator(utt):
        return confirmation_str in utt
    return wrapped_validator


def voc_confirmation_validator(confirmation_voc: str, skill: MycroftSkill):
    """
    Returns a validator method that returns true if the confirmation_voc vocab resource is in the passed string.
    :param confirmation_voc: vocab resource to locate in utterance
    :param skill: skill with access to the passed vocab
    :return: True if the confirmation is in the spoken utterance.
    """
    if not isinstance(confirmation_voc, str):
        raise TypeError(f"Expected str, got {type(confirmation_voc)}")
    if not skill.find_resource(f"{confirmation_voc}.voc"):
        raise FileNotFoundError(f"Could not locate requested vocab: {confirmation_voc}")

    def wrapped_validator(utt):
        return skill.voc_match(utt, confirmation_voc)
    return wrapped_validator

