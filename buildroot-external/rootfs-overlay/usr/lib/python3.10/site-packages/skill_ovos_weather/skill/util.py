# Copyright 2021, Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions for the weather skill."""
from datetime import datetime, timedelta, tzinfo
from time import time

import pytz

from mycroft.api import GeolocationApi
from mycroft.util.format import nice_date
from mycroft.util.parse import extract_datetime
from mycroft.util.time import now_local


class LocationNotFoundError(ValueError):
    """Raise when the API cannot find the requested location."""

    pass


def convert_to_local_datetime(timestamp: time, timezone: str) -> datetime:
    """Convert a timestamp to a datetime object in the requested timezone.

    This function assumes it is passed a timestamp in the UTC timezone.  It
    then adjusts the datetime to match the specified timezone.

    Args:
        timestamp: seconds since epoch
        timezone: the timezone requested by the user

    Returns:
        A datetime in the passed timezone based on the passed timestamp
    """
    naive_datetime = datetime.fromtimestamp(timestamp)
    utc_datetime = pytz.utc.localize(naive_datetime)
    local_timezone = pytz.timezone(timezone)
    local_datetime = utc_datetime.astimezone(local_timezone)

    return local_datetime


def get_utterance_datetime(
    utterance: str, timezone: str = None, language: str = None
) -> datetime:
    """Get a datetime representation of a date or time concept in an utterance.

    Args:
        utterance: the words spoken by the user
        timezone: the timezone requested by the user
        language: the language configured on the device

    Returns:
        The date and time represented in the utterance in the specified timezone.
    """
    utterance_datetime = None
    if timezone is None:
        anchor_date = None
    else:
        intent_timezone = get_tz_info(timezone)
        anchor_date = datetime.now(intent_timezone)
    extract = extract_datetime(utterance, anchor_date, language)
    if extract is not None:
        utterance_datetime, _ = extract

    return utterance_datetime


def get_tz_info(timezone: str) -> tzinfo:
    """Generate a tzinfo object from a timezone string.

    Args:
        timezone: a string representing a timezone

    Returns:
        timezone in a string format
    """
    return pytz.timezone(timezone)


def get_geolocation(location: str):
    """Retrieve the geolocation information about the requested location.

    Args:
        location: a location specified in the utterance

    Returns:
        A deserialized JSON object containing geolocation information for the
        specified city.

    Raises:
        LocationNotFound error if the API returns no results.
    """
    geolocation_api = GeolocationApi()
    geolocation = geolocation_api.get_geolocation(location)

    if geolocation is None:
        raise LocationNotFoundError("Location {} is unknown".format(location))

    return geolocation


def get_time_period(intent_datetime: datetime) -> str:
    """Translate a specific time '9am' to period of the day 'morning'

    Args:
        intent_datetime: the datetime extracted from an utterance

    Returns:
        A generalized time of day based on the passed datetime object.
    """
    hour = intent_datetime.time().hour
    if 1 <= hour < 5:
        period = "early morning"
    elif 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    elif 17 <= hour < 20:
        period = "evening"
    else:
        period = "overnight"

    return period


def get_speakable_day_of_week(date_to_speak: datetime):
    """Convert the time of the a daily weather forecast to a speakable day of week.

    Args:
        date_to_speak: The date/time for the forecast being reported.

    Returns:
        The day of the week in the device's configured language
    """
    now = now_local()
    tomorrow = now.date() + timedelta(days=1)

    # A little hack to prevent nice_date() from returning "tomorrow"
    if date_to_speak.date() == tomorrow:
        now_arg = now - timedelta(days=1)
    else:
        now_arg = now

    speakable_date = nice_date(date_to_speak, now=now_arg)
    day_of_week = speakable_date.split(",")[0]

    return day_of_week
