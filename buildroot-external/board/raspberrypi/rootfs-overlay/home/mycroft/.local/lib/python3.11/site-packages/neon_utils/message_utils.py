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

import base64
import inspect

from enum import Enum
from time import time
from typing import Optional, Union
from mycroft_bus_client import Message
from neon_utils.logger import LOG


class MessageKind(Enum):
    SPEAK = "speak"
    DATA = "skills:execute.utterance"
    EXECUTE = "skills:execute.utterance"


class EncodingError(ValueError):
    """Exception to indicate an invalid Encoding"""


def request_from_mobile(message: Message) -> bool:
    """
    Check if a request is from a mobile device
    Args:
        message: Message object associated with request

    Returns:
        True if message is from a mobile app, else False
    """
    return message.context.get("mobile", False)


def get_message_user(message: Message) -> Optional[str]:
    """
    Get the user associated with a message
    Args:
        message: Message object associated with request

    Returns:
        Username associated with message
    """
    if not message:
        raise ValueError
    if not hasattr(message, "context"):
        raise AttributeError(type(message))
    return message.context.get("username")


def encode_bytes_to_b64_string(data: bytes, charset: str = "utf-8") -> str:
    """
    Encode a bytes object into a string that can be passed on the messagebus
    :param data: bytes data to be encoded
    :param charset: character set to decode b64 bytes (https://docs.python.org/3/library/codecs.html#standard-encodings)
    :return: base64 encoded string
    """
    if not data or not isinstance(data, bytes):
        raise ValueError(f"Invalid data provided to be encoded. type={type(data)}")

    encoded = base64.b64encode(data)

    try:
        bytestr = encoded.decode(charset)
    except LookupError:
        raise EncodingError(f"Invalid charset provided: {charset}")

    return bytestr


def decode_b64_string_to_bytes(data: str, charset: str = "utf-8") -> bytes:
    """
    Decodes a base64-encoded string to bytes
    :param data: string encoded data to decode
    :param charset: character set of b64 string (https://docs.python.org/3/library/codecs.html#standard-encodings)
    :return: decoded bytes object
    """
    if not data or not isinstance(data, str):
        raise ValueError(f"Invalid data provided to be encoded. type={type(data)}")

    try:
        byte_data = data.encode(charset)
    except LookupError:
        raise EncodingError(f"Invalid charset provided: {charset}")

    encoded = base64.b64decode(byte_data)

    if not encoded:
        raise EncodingError(f"Invalid charset provided for data. charset={charset}")

    return encoded


def dig_for_message(max_records: int = 10) -> Optional[Message]:
    """
    Dig Through the stack for message. Looks at the current stack for a passed argument of type 'Message'
    :param max_records: Maximum number of stack records to look through
    :return: Message if found in args, else None
    """
    stack = inspect.stack()[1:]  # First frame will be this function call
    stack = stack if len(stack) <= max_records else stack[:max_records]
    for record in stack:
        args = inspect.getargvalues(record.frame)
        if args.args:
            for arg in args.args:
                if isinstance(args.locals[arg], Message):
                    return args.locals[arg]
    return None


def resolve_message(function):
    """
    Decorator to try and fill an optional `message` kwarg
    """
    def wrapper(*args, **kwargs):
        params = inspect.signature(function).parameters
        if not any([param in params for param in ("message", "kwargs")]):
            LOG.warning("Decorated function does not expect a `message`")
            return function(*args, **kwargs)

        if "message" in params.keys() and len(args):
            i = 0
            for param in params:
                args = list(args)
                # Check if 'message' is filled by an arg
                if param == "message" and i < len(args):
                    if not args[i]:
                        args[i] = dig_for_message(50)
                        return function(*args, **kwargs)
                i += 1

        if not kwargs.get("message") and not any([arg for arg in args if
                                                  isinstance(arg, Message)]):
            if LOG.diagnostic_mode:
                call = inspect.stack()[1]
                module = inspect.getmodule(call.frame)
                name = module.__name__ if module else call.filename
                LOG.debug(f"Digging for requested message arg - "
                          f"{name}:{call.lineno}")
            message = dig_for_message(50)
            kwargs["message"] = message
        return function(*args, **kwargs)

    return wrapper


@resolve_message
def request_for_neon(message: Message = None,
                     activation_voc: Optional[str] = "neon",
                     voc_match: Optional[callable] = None,
                     ww_enabled: bool = True) -> bool:
    """
    Check if a wake word or activation word is present in a request
    :param message: Message to evaluate
    :param activation_voc: vocab of activation word for the assistant
    :param voc_match: `skill.voc_match` method to check for `activation_voc`
    :param ww_enabled: True if WW is required for STT system-wide
    :returns: True if the message contains an activation word
    """
    if not message:
        raise ValueError("message not provided and not resolvable")
    if message.context.get('neon_should_respond'):
        return True
    if activation_voc in message.data:
        return True

    server_request = message.context.get('klat_data')

    if ww_enabled and not server_request:
        # TODO: WW should add to message context instead DM
        return True

    # Check Klat conversation context
    if server_request and \
            server_request.get('title', '').startswith("!PRIVATE"):
        return True

    # Check for voc_match if method provided
    try:
        if voc_match and voc_match(message.data.get('utterance', '').lower(),
                                   activation_voc):
            return True
    except FileNotFoundError as e:
        LOG.error(e)

    return False


@resolve_message
def build_message(kind: Union[MessageKind, str], utt: str, message: Message,
                  speaker: Optional[dict] = None) -> Message:
    """
    Build a message object for skill execution or TTS output
    :param kind: "neon speak" or "execute"
    :param utt: string to emit
    :param message: incoming message object
    :param speaker: speaker data dictionary
    :return: Message object
    """
    from neon_utils.user_utils import get_user_prefs
    if isinstance(kind, str):
        kind = MessageKind.EXECUTE if kind == "execute" else \
            MessageKind.DATA if kind == "skill_data" else MessageKind.SPEAK

    default_speech = get_user_prefs(message)["speech"]
    speaker = speaker or {"name": "Neon",
                          "language": default_speech["tts_language"],
                          "gender": default_speech["tts_gender"],
                          "voice": default_speech["neon_voice"],
                          "override_user": True}
    if speaker.get("language"):
        speaker['override_user'] = True

    if kind in (MessageKind.EXECUTE, MessageKind.DATA):
        return message.reply(kind.value, {
            "utterances": [utt.lower()],
            "lang": message.data.get("lang", "en-US"),
            "session": None,
            "ident": time(),
            "speaker": speaker
        }, {
            "neon_should_respond": True,
            "cc_data": {"request": utt,
                        "emit_response": kind == MessageKind.DATA,
                        "execute_from_script": True
                        }
        })
    elif kind == MessageKind.SPEAK:
        added_context = {"cc_data": message.context.get("cc_data", {})}
        added_context["cc_data"]["request"] = utt

        return message.reply(kind.value, {"utterance": utt,
                                          "lang": message.data.get("lang",
                                                                   "en-US"),
                                          "speaker": speaker
                                          }, {**message.context,
                                              **added_context})
