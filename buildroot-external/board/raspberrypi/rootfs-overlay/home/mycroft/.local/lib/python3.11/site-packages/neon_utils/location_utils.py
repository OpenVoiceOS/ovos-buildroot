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

from datetime import datetime
from typing import Optional, Union

import pendulum

from dateutil.tz import tzlocal, gettz
from geopy.exc import GeocoderServiceError

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from neon_utils.logger import LOG


def get_full_location(address: Union[str, tuple],
                      lang: Optional[str] = None) -> Optional[dict]:
    """
    Get full location details for the specified address in the specified lang
    :param address: string address or tuple (latitude, longitude)
    :param lang: optional language to format results (else system default)
    :returns: dict containing at minimum `place_id`, `lat`, `lon`, `address`
        None if service is not available
    """
    try:
        nominatim = Nominatim(user_agent="neon-ai")
        if isinstance(address, str):
            location = nominatim.geocode(address, addressdetails=True,
                                         language=lang)
        else:
            location = nominatim.reverse(address, addressdetails=True,
                                         language=lang)
        return location.raw
    except GeocoderServiceError as e:
        LOG.error(e)
    except Exception as e:
        LOG.exception(e)
    return None


def get_coordinates(gps_loc: dict) -> (float, float):
    """
    Gets the latitude and longitude for the passed location
    :param gps_loc: dict of "city", "state", "country"
    :return: lat, lng float values
    """
    coordinates = Nominatim(user_agent="neon-ai")
    try:
        location = coordinates.geocode(gps_loc)
        LOG.debug(f"{location}")
        return location.latitude, location.longitude
    except Exception as x:
        LOG.error(x)
        return -1, -1


def get_location(lat, lng) -> (str, str, str, str):
    """
    Gets location name values for the passed coordinates.
    Note that some coordinates do not have a city, but may have a county.
    :param lat: latitude
    :param lng: longitude
    :return: city, county, state, country
    """
    address = Nominatim(user_agent="neon-ai")
    location = address.reverse([lat, lng], language="en-US")
    LOG.debug(f"{location}")
    LOG.debug(f"{location.raw}")
    LOG.debug(f"{location.raw.get('address')}")
    city = location.raw.get('address').get('city') or location.raw.get('address').get('town')
    county = location.raw.get('address').get('county')
    state = location.raw.get('address').get('state')
    country = location.raw.get('address').get('country')
    return city, county, state, country


def get_timezone(lat, lng) -> (str, float):
    """
    Gets timezone information for the passed coordinates.
    Note that some coordinates do not have a city, but may have a county.
    :param lat: latitude
    :param lng: longitude
    :return: timezone name, offset from GMT
    """
    timezone = TimezoneFinder().timezone_at(lng=float(lng), lat=float(lat))
    offset = pendulum.from_timestamp(0, timezone).offset_hours
    return timezone, offset


def to_system_time(dt: datetime) -> datetime:
    """
    Converts a timezone aware or timezone naiive datetime object to a datetime object in the system tz
    :param dt: datetime object to convert
    :return: timezone aware datetime object that can be scheduled
    """
    tz = tzlocal()
    if dt.tzinfo:
        return dt.astimezone(tz)
    else:
        return dt.replace(tzinfo=tz).astimezone(tz)
