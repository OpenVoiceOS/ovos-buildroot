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
#
import json
import random

from flask import make_response
from ovos_utils.log import LOG
from ovos_utils.ovos_service_api import OvosWolframAlpha, OvosWeather
from ovos_backend_client.api import GeolocationApi, WolframAlphaApi, OpenWeatherMapApi

from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.session import SESSION as requests
from ovos_local_backend.utils.geolocate import get_timezone, Geocoder


def generate_code():
    k = ""
    while len(k) < 6:
        k += random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I",
                            "J", "K", "L", "M", "N", "O", "P", "Q", "R",
                            "S", "T", "U", "Y", "V", "X", "W", "Z", "0",
                            "1", "2", "3", "4", "5", "6", "7", "8", "9"])
    return k.upper()


def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys=True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response


def to_camel_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + ''.join(x.title() for x in components[1:])


def dict_to_camel_case(data):
    converted = {}
    for k, v in data.items():
        new_k = to_camel_case(k)
        if isinstance(v, dict):
            v = dict_to_camel_case(v)
        if isinstance(v, list):
            for idx, item in enumerate(v):
                if isinstance(item, dict):
                    v[idx] = dict_to_camel_case(item)
        converted[new_k] = v
    return converted


class ExternalApiManager:
    def __init__(self):
        self.config = CONFIGURATION.get("microservices", {})
        self.units = CONFIGURATION["system_unit"]

        self.wolfram_key = self.config.get("wolfram_key")
        self.owm_key = self.config.get("owm_key")

        if self.owm_key:
            self.local_owm = LocalWeather(self.owm_key)
        else:
            self.local_owm = None

        self.ovos_wolfram = OvosWolframAlpha()
        self.ovos_owm = OvosWeather()
        if not self.ovos_owm.uuid:
            try:
                self.ovos_owm.api.register_device()
            except Exception as e:
                LOG.debug(f"Error registering device {e}")
        self.geo = Geocoder()

        self.selene_owm = None
        self.selene_wolf = None
        self.selene_cfg = CONFIGURATION.get("selene") or {}
        if self.selene_cfg.get("enabled"):
            _url = self.selene_cfg.get("url")
            _version = self.selene_cfg.get("version") or "v1"
            _identity_file = self.selene_cfg.get("identity_file")
            self.selene_owm = OpenWeatherMapApi(_url, _version, _identity_file)
            self.selene_wolfram = WolframAlphaApi(_url, _version, _identity_file)

    @property
    def _owm(self):
        if self.config.get("weather_provider") == "local":
            if self.owm_key:
                return self.local_owm
            if self.config.get("ovos_fallback"):
                return self.ovos_owm
        elif self.config.get("weather_provider") == "ovos":
            return self.ovos_owm
        elif self.config.get("weather_provider") == "selene":
            if self.selene_owm:
                return self.selene_owm
            if self.config.get("ovos_fallback"):
                return self.ovos_owm
        else:  # auto
            if self.owm_key:
                return self.local_owm
            if self.selene_owm:
                return self.selene_owm
            return self.ovos_owm

    @property
    def _wolfram(self):
        if self.config.get("wolfram_provider") == "local":
            if self.wolfram_key:
                return LocalWolfram(self.wolfram_key)
            if self.config.get("ovos_fallback"):
                return self.ovos_wolfram
        elif self.config.get("wolfram_provider") == "ovos":
            return self.ovos_wolfram
        elif self.config.get("wolfram_provider") == "selene":
            if self.selene_wolfram:
                return self.selene_wolfram
            if self.config.get("ovos_fallback"):
                return self.ovos_wolfram
        else:  # auto
            if self.wolfram_key:
                return LocalWolfram(self.wolfram_key)
            if self.selene_wolfram:
                return self.selene_wolfram
            return self.ovos_wolfram

    def geolocate(self, address):
        data = self.geo.get_location(address)
        return {"data": {
            "city": data["city"],
            "country": data["country"],
            "latitude": float(data["lat"]),
            "longitude": float(data["lon"]),
            "region": data["region"],
            "timezone": get_timezone(float(data["lat"]), float(data["lon"]))
        }}

    def wolfram_spoken(self, query, units=None, lat_lon=None):
        units = units or self.units
        if units != "metric":
            units = "imperial"
        if isinstance(self._wolfram, LocalWolfram) or \
                isinstance(self._wolfram, WolframAlphaApi):  # local + selene
            # TODO - lat lon, not used? selene accepts it but....
            # https://products.wolframalpha.com/spoken-results-api/documentation/
            return self._wolfram.spoken(query, units)
        if hasattr(self._wolfram, "get_wolfram_spoken"):  # ovos api
            q = {"input": query, "units": units}
            return self._wolfram.get_wolfram_spoken(q)

    def wolfram_simple(self, query, units=None, lat_lon=None):
        units = units or self.units
        if units != "metric":
            units = "imperial"
        if isinstance(self._wolfram, LocalWolfram) or \
                isinstance(self._wolfram, WolframAlphaApi):  # local + selene
            return self._wolfram.simple(query, units)
        if isinstance(self._wolfram, OvosWolframAlpha):  # ovos api
            q = {"input": query, "units": units}
            return self._wolfram.get_wolfram_simple(q)

    def wolfram_full(self, query, units=None, lat_lon=None):
        units = units or self.units
        if units != "metric":
            units = "imperial"
        if isinstance(self._wolfram, LocalWolfram):
            return self._wolfram.full(query, units)
        if isinstance(self._wolfram, WolframAlphaApi):  # selene
            return self._wolfram.full_results(query, units, lat_lon, {"output": "json"})
        if isinstance(self._wolfram, OvosWolframAlpha):  # ovos api
            q = {"input": query, "units": units}
            return self._wolfram.get_wolfram_full(q)

    def wolfram_xml(self, query, units=None, lat_lon=None):
        units = units or self.units
        if units != "metric":
            units = "imperial"
        if isinstance(self._wolfram, LocalWolfram):
            return self._wolfram.full(query, units, output="xml")
        if isinstance(self._wolfram, WolframAlphaApi):
            return self._wolfram.full_results(query, units, lat_lon, {"output": "xml"})
        if isinstance(self._wolfram, OvosWolframAlpha):
            q = {"input": query, "units": units, "output": "xml"}
            return self._wolfram.get_wolfram_full(q)

    def owm_current(self, lat, lon, units, lang="en-us"):
        if isinstance(self._owm, LocalWeather):  # local
            return self._owm.current(lat, lon, units, lang)
        if isinstance(self._owm, OvosWeather):  # ovos
            params = {"lang": lang, "units": units, "lat": lat, "lon": lon}
            return self._owm.get_current(params)
        if isinstance(self._owm, OpenWeatherMapApi):  # selene
            return self._owm.get_current((lat, lon), lang, units)

    def owm_onecall(self, lat, lon, units, lang="en-us"):
        if isinstance(self._owm, LocalWeather):  # local
            return self._owm.onecall(lat, lon, units, lang)
        if isinstance(self._owm, OvosWeather):  # ovos
            params = {"lang": lang, "units": units, "lat": lat, "lon": lon}
            return self._owm.get_weather_onecall(params)
        if isinstance(self._owm, OpenWeatherMapApi):  # selene
            return self._owm.get_weather((lat, lon), lang, units)

    def owm_hourly(self, lat, lon, units, lang="en-us"):
        if isinstance(self._owm, LocalWeather):  # local
            return self._owm.hourly(lat, lon, units, lang)
        if isinstance(self._owm, OvosWeather):  # ovos
            params = {"lang": lang, "units": units, "lat": lat, "lon": lon}
            return self._owm.get_hourly(params)
        if isinstance(self._owm, OpenWeatherMapApi):  # selene
            return self._owm.get_hourly((lat, lon), lang, units)

    def owm_daily(self, lat, lon, units, lang="en-us"):
        if isinstance(self._owm, LocalWeather):  # local
            return self._owm.daily(lat, lon, units, lang)
        if isinstance(self._owm, OvosWeather):  # ovos
            params = {"lang": lang, "units": units, "lat": lat, "lon": lon}
            return self._owm.get_forecast(params)
        if isinstance(self._owm, OpenWeatherMapApi):  # selene
            return self._owm.get_daily((lat, lon), lang, units)


class LocalWeather:
    def __init__(self, key):
        self.key = key

    def current(self, lat, lon, units, lang):
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.key
        }
        url = "https://api.openweathermap.org/data/2.5/weather"
        return requests.get(url, params=params).json()

    def daily(self, lat, lon, units, lang):
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.key
        }
        url = "https://api.openweathermap.org/data/2.5/forecast/daily"
        return requests.get(url, params=params).json()

    def hourly(self, lat, lon, units, lang):
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.key
        }
        url = "https://api.openweathermap.org/data/2.5/forecast"
        return requests.get(url, params=params).json()

    def onecall(self, lat, lon, units, lang):
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.key
        }
        url = "https://api.openweathermap.org/data/2.5/onecall"
        return requests.get(url, params=params).json()


class LocalWolfram:
    def __init__(self, key):
        self.key = key

    def spoken(self, query, units):
        url = 'https://api.wolframalpha.com/v1/spoken'
        params = {"appid": self.key,
                  "i": query,
                  "units": units}
        answer = requests.get(url, params=params).text
        return answer

    def simple(self, query, units):
        url = 'https://api.wolframalpha.com/v1/simple'
        params = {"appid": self.key,
                  "i": query,
                  "units": units}
        answer = requests.get(url, params=params).text
        return answer

    def full(self, query, units, output="json"):
        url = 'https://api.wolframalpha.com/v2/query'
        params = {"appid": self.key,
                  "input": query,
                  "output": output,
                  "units": units}
        answer = requests.get(url, params=params).json()
        return answer
