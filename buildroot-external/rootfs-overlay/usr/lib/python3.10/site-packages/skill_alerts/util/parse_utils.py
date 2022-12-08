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
import datetime as dt
import os.path

from time import time
from uuid import uuid4 as uuid
from typing import Optional, List, Union
from lingua_franca import load_language
from neon_utils.logger import LOG
from mycroft_bus_client import Message, MessageBusClient

from mycroft.util.format import TimeResolution, nice_duration, nice_time
from mycroft.util.parse import extract_datetime, extract_duration, normalize

from . import AlertPriority, Weekdays, AlertType
from .alert import Alert
from .alert_manager import _DEFAULT_USER

_SCRIPT_PRIORITY = AlertPriority.HIGHEST
_default_lang = "en-US"


def _default_find_resource(res_name, _=None, lang=None):
    LOG.warning("find_resource method not defined, using fallback")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    lang = lang or "en-us"
    file = os.path.join(base_dir, "locale", lang, res_name)
    if os.path.isfile(file):
        return file
    return None


def _default_spoken(alert_type: AlertType):
    LOG.warning("get_spoken_alert_type method not defined, using fallback")
    if alert_type == AlertType.ALARM:
        return "alarm"
    if alert_type == AlertType.TIMER:
        return "timer"
    if alert_type == AlertType.REMINDER:
        return "reminder"
    return "alert"


def round_nearest_minute(alert_time: dt.datetime,
                         cutoff: dt.timedelta = dt.timedelta(minutes=10)) -> \
        dt.datetime:
    """
    Round an alert time to the nearest minute if it is longer than the cutoff
    :param alert_time: requested alert datetime
    :param cutoff: minimum delta to consider rounding the alert time
    :returns: datetime rounded to the nearest minute if delta exceeds cutoff
    """
    if alert_time <= dt.datetime.now(dt.timezone.utc) + cutoff:
        return alert_time
    else:
        new_alert_time = alert_time.replace(second=0).replace(microsecond=0)
    return new_alert_time


def spoken_time_remaining(alert_time: dt.datetime,
                          now_time: Optional[dt.datetime] = None,
                          lang=_default_lang) -> str:
    """
    Gets a speakable string representing time until alert_time
    :param alert_time: Datetime to get duration until
    :param now_time: Datetime to count duration from
    :param lang: Language to format response in
    :return: speakable duration string
    """
    load_language(lang or _default_lang)
    now_time = now_time or dt.datetime.now(dt.timezone.utc)
    remaining_time: dt.timedelta = alert_time - now_time

    if remaining_time > dt.timedelta(weeks=1):
        resolution = TimeResolution.DAYS
    elif remaining_time > dt.timedelta(days=1):
        resolution = TimeResolution.HOURS
    elif remaining_time > dt.timedelta(hours=1):
        resolution = TimeResolution.MINUTES
    else:
        resolution = TimeResolution.SECONDS
    return nice_duration(remaining_time.total_seconds(),
                         resolution=resolution, lang=lang)


def get_default_alert_name(alert_time: dt.datetime, alert_type: AlertType,
                           now_time: Optional[dt.datetime] = None,
                           lang: str = None, use_24hour: bool = False,
                           spoken_alert_type: callable = _default_spoken) -> \
        str:
    """
    Build a default name for the specified alert
    :param alert_time: datetime of next alert expiration
    :param alert_type: AlertType of alert to name
    :param now_time: datetime to anchor timers for duration
    :param lang: Language to format response in
    :param use_24hour: If true, use 24 hour timescale
    :param spoken_alert_type: method to translate AlertType to speakable string
    :return: name for alert
    """
    lang = lang or _default_lang
    if alert_type == AlertType.TIMER:
        time_str = spoken_time_remaining(alert_time, now_time, lang)
    else:
        load_language(lang)
        time_str = nice_time(alert_time, lang, False, use_24hour, True)
    return f"{time_str} {spoken_alert_type(alert_type)}"


def build_alert_from_intent(message: Message, alert_type: AlertType,
                            timezone: dt.tzinfo, use_24hour: bool = False,
                            get_spoken_alert_type: callable = _default_spoken,
                            find_resource: callable = _default_find_resource) \
        -> Optional[Alert]:
    """
    Parse alert parameters from a matched intent into an Alert object
    :param message: Message associated with request
    :param alert_type: AlertType requested
    :param timezone: Timezone for user associated with request
    :param use_24hour: Use 24 hour time format if True, else 12 hour
    :param get_spoken_alert_type: optional method to get translated alert types
    :param find_resource: skill.find_resource method to resolve resource files
    :returns: Alert extracted from utterance or None if missing required params
    """
    tokens = tokenize_utterance(message)
    repeat = parse_repeat_from_message(message, tokens)
    if isinstance(repeat, dt.timedelta):
        repeat_interval = repeat
        repeat_days = None
    else:
        repeat_days = repeat
        repeat_interval = None

    # Parse data in a specific order since tokens are mutated in parse methods
    priority = parse_alert_priority_from_message(message, tokens)
    end_condition = parse_end_condition_from_message(message, tokens, timezone)
    audio_file = parse_audio_file_from_message(message, tokens)
    script_file = parse_script_file_from_message(message, tokens)
    anchor_time = dt.datetime.now(timezone)
    alert_time = parse_alert_time_from_message(message, tokens, timezone, anchor_time)

    if not alert_time:
        if repeat_interval:
            alert_time = anchor_time + repeat_interval
        else:
            return

    lang = message.data.get("lang")
    try:
        article_file = find_resource("articles.voc", lang=lang)
    except TypeError:
        LOG.error("Incompatible `find_resource` method passed")
        article_file = _default_find_resource("articles.voc", lang=lang)
    if article_file:
        with open(article_file) as f:
            articles = f.read().split('\n')
    else:
        articles = list()
    alert_context = parse_alert_context_from_message(message)
    alert_context['start_time'] = anchor_time.isoformat()
    alert_name = parse_alert_name_from_message(message, tokens, True,
                                               articles) or \
        get_default_alert_name(alert_time, alert_type, anchor_time, lang,
                               use_24hour, get_spoken_alert_type)

    alert = Alert.create(alert_time, alert_name, alert_type, priority,
                         repeat_interval, repeat_days, end_condition,
                         audio_file, script_file, alert_context)
    return alert


def tokenize_utterance(message: Message) -> List[str]:
    """
    Get utterance tokens, split on matched vocab
    :param message: Message associated with intent match
    :returns: list of utterance tokens where a tag defines a token
    """
    utterance = message.data["utterance"]
    tags = message.data["__tags__"]
    tags.sort(key=lambda tag: tag["start_token"])
    extracted_words = [tag.get("match") for tag in tags]

    chunks = list()
    for word in extracted_words:
        parsed, utterance = utterance.split(word, 1)
        chunks.extend((parsed, word))
    chunks.append(utterance)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks


def get_unmatched_tokens(message: Message,
                         tokens: Optional[list] = None) -> List[str]:
    """
    Strips the matched intent keywords from the utterance and returns the
    remaining tokens
    :param message: Message associated with intent match
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :returns: list of tokens not associated with intent vocab
    """
    tokens = tokens or tokenize_utterance(message)
    unmatched = [chunk for chunk in tokens if
                 not any([tag["match"] == chunk
                          for tag in message.data["__tags__"]])]
    return unmatched


def parse_repeat_from_message(message: Message,
                              tokens: Optional[list] = None) -> \
        Union[List[Weekdays], dt.timedelta]:
    """
    Parses a repeat clause from the utterance. If tokens are provided, handled
    tokens are removed.
    :param message: Message associated with intent match
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :returns: list of parsed repeat Weekdays or timedelta between occurrences
    """
    repeat_days = list()
    lang = message.data.get("lang", "en-us")
    load_language(lang)
    if message.data.get("everyday"):
        repeat_days = [Weekdays(i) for i in range(0, 7)]
    elif message.data.get("weekends"):
        repeat_days = [Weekdays(i) for i in (5, 6)]
    elif message.data.get("weekdays"):
        repeat_days = [Weekdays(i) for i in range(0, 5)]
    elif message.data.get("repeat"):
        tokens = tokens or tokenize_utterance(message)
        repeat_index = tokens.index(message.data["repeat"]) + 1
        repeat_clause = tokens.pop(repeat_index)
        repeat_days = list()
        remainder = ""
        default_time = dt.time()
        # Parse repeat days
        for word in repeat_clause.split():  # Iterate over possible weekdays
            if word.isnumeric():
                # Don't try to parse time intervals
                remainder += f' {word}'
                continue
            extracted_content = extract_datetime(word)
            if not extracted_content:
                remainder += f' {word}'
                continue
            extracted_dt = extracted_content[0]
            if extracted_dt.time() == default_time:
                repeat_days.append(Weekdays(extracted_dt.weekday()))
                remainder += '\n'
            else:
                remainder += f' {word}'

        # Parse repeat interval
        if not repeat_days:
            extracted_duration = extract_duration(repeat_clause, lang)
            if extracted_duration and not extracted_duration[0]:
                # Replace "the next week" with "1 week", etc.
                extracted_duration = extract_duration(
                    f"1 {extracted_duration[1]}", lang)
            if extracted_duration and extracted_duration[0]:
                duration, remainder = extracted_duration
                if remainder and remainder.strip():
                    tokens.insert(repeat_index, remainder.strip())
                return duration

        if remainder:
            new_tokens = remainder.split('\n')
            for token in new_tokens:
                if token.strip():
                    tokens.insert(repeat_index, token.strip())
                    repeat_index += 1
    return repeat_days


def parse_end_condition_from_message(message: Message,
                                     tokens: Optional[list] = None,
                                     timezone: dt.tzinfo = dt.timezone.utc) \
        -> Optional[dt.datetime]:
    """
    Parses an end condition from the utterance. If tokens are provided, handled
    tokens are removed.
    :param message: Message associated with intent match
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :param timezone: timezone of request, defaults to utc
    :returns: extracted datetime of end condition, else None
    """
    tokens = tokens or tokenize_utterance(message)
    anchor_date = dt.datetime.now(timezone)

    if message.data.get("until"):
        lang = message.data.get("lang") or "en-us"
        load_language(lang)
        idx = tokens.index(message.data["until"]) + 1
        end_clause = tokens.pop(idx)

        end_time = None
        extracted_dt = extract_datetime(end_clause, anchor_date, lang)
        if extracted_dt:
            end_time, remainder = extracted_dt
            tokens.insert(idx, remainder)
        else:
            extracted_duration = extract_duration(end_clause, lang)
            if extracted_duration and not extracted_duration[0]:
                # Replace "the next week" with "1 week", etc.
                extracted_duration = extract_duration(
                    f"1 {extracted_duration[1]}", lang)
            if extracted_duration and extracted_duration[0]:
                duration, remainder = extracted_duration
                tokens.insert(idx, remainder)
                end_time = anchor_date + duration
        return end_time

    return None


def parse_alert_time_from_message(message: Message,
                                  tokens: Optional[list] = None,
                                  timezone: dt.tzinfo = dt.timezone.utc,
                                  anchor_time: dt.datetime = None) -> \
        Optional[dt.datetime]:
    """
    Parse a requested alert time from the request utterance
    :param message: Message associated with intent match
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :param timezone: timezone of request, defaults to utc
    :returns: Parsed datetime for the alert or None if no time is extracted
    """
    anchor_time = anchor_time or dt.datetime.now(timezone)
    tokens = tokens or tokenize_utterance(message)
    remainder_tokens = get_unmatched_tokens(message, tokens)
    load_language(message.data.get("lang") or _default_lang)
    alert_time = None
    for token in remainder_tokens:
        extracted = extract_duration(token)
        if extracted and extracted[0]:
            duration, remainder = extracted
            alert_time = anchor_time + duration
            tokens[tokens.index(token)] = remainder
            break
        extracted = extract_datetime(token, anchorDate=anchor_time)
        if extracted and extracted[0]:
            alert_time, remainder = extracted
            tokens[tokens.index(token)] = remainder
            break
    return alert_time


def parse_audio_file_from_message(message: Message,
                                  tokens: Optional[list] = None) -> \
        Optional[str]:
    """
    Parses a requested audiofile from the utterance. If tokens are provided,
    handled tokens are removed.
    :param message: Message associated with intent match
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :returns: extracted audio file path, else None
    """
    if message.data.get("playable"):
        # TODO: Parse an audio filename here and remove matched token
        pass
    return None


def parse_script_file_from_message(message: Message,
                                   tokens: Optional[list] = None,
                                   bus: MessageBusClient = None) -> \
        Optional[str]:
    """
    Parses a requested script file from the utterance. If tokens are provided,
    handled tokens are removed.
    :param message: Message associated with intent match
    :param bus: Connected MessageBusClient to query available scripts
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :returns: validated script filename, else None
    """
    bus = bus or MessageBusClient()
    if not bus.started_running:
        bus.run_in_thread()
    if message.data.get("script"):
        # TODO: Validate/test this DM
        # check if CC can access the required script and get its valid name
        resp = bus.wait_for_response(Message("neon.script_exists",
                                             data=message.data,
                                             context=message.context))
        is_valid = resp.data.get("script_exists", False)
        consumed = resp.data.get("consumed_utt", "")
        if tokens and consumed:
            for token in tokens:
                if consumed in token:
                    # TODO: Split on consumed words and insert unmatched tokens
                    pass
        return resp.data.get("script_name", None) if is_valid else None
    return None


def parse_alert_priority_from_message(message: Message,
                                      tokens: Optional[list] = None) -> \
        AlertPriority:
    """
    Extract the requested alert priority from intent message.
    If tokens are provided, handled tokens are removed.
    :param message: Message associated with request
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    """
    # TODO: Parse requested priority from utterance
    if message.data.get("script"):
        priority = _SCRIPT_PRIORITY
    else:
        priority = AlertPriority.AVERAGE
    return priority


def parse_alert_name_from_message(message: Message,
                                  tokens: Optional[list] = None,
                                  strip_datetimes: bool = False,
                                  articles: List[str] = None) -> \
        Optional[str]:
    """
    Try to parse an alert name from unparsed tokens
    :param message: Message associated with the request
    :param tokens: optional tokens parsed from message by `tokenize_utterances`
    :param strip_datetimes: if True, ignore any passed tokens containing times
    :param articles: list of words to strip from a candidate alert name
    :returns: Best guess at a name extracted from tokens
    """
    def _strip_datetime_from_token(t):
        try:
            _, t = extract_duration(t, lang)
        except TypeError:
            pass
        try:
            _, t = extract_datetime(t, lang=lang)
        except TypeError:
            pass
        return t

    specified_tokens = tokens
    lang = message.data.get("lang") or "en-us"
    articles = articles or list()

    load_language(lang)
    candidate_names = list()
    # First try to parse a name from the remainder tokens
    tokens = get_unmatched_tokens(message, tokens)
    for token in tokens:
        if strip_datetimes:
            token = _strip_datetime_from_token(token)
        normalized = " ".join([word for word in normalize(token, lang).split()
                               if word not in articles])
        if normalized:
            candidate_names.append(normalized)
    # Next try to extract a name from the full tokenized utterance
    if not candidate_names and specified_tokens:
        LOG.info("No possible names parsed, checking all tokens")
        all_untagged_tokens = get_unmatched_tokens(message)
        for token in all_untagged_tokens:
            token = _strip_datetime_from_token(token)
            normalized = " ".join([word for word in
                                   normalize(token, lang).split()
                                   if word not in articles])
            if normalized:
                candidate_names.append(normalized)
    if not candidate_names:
        return None
    LOG.info(f"Parsed possible names: {candidate_names}")
    return candidate_names[0]


def parse_alert_context_from_message(message: Message) -> dict:
    """
    Parse the request message context and ensure required parameters exist
    :param message: Message associated with the request
    :returns: dict context to include in Alert object
    """
    required_context = {
        "user": message.context.get("user") or _DEFAULT_USER,
        "ident": message.context.get("ident") or str(uuid()),
        "created": message.context.get("timing",
                                       {}).get("handle_utterance") or time()
    }
    return {**message.context, **required_context}
