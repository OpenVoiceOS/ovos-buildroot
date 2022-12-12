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
"""Call the Open Weather Map One Call API through Selene.

The One Call API provides current weather, 48 hourly forecasts, 7 daily forecasts
and weather alert data all in a single API call.  The endpoint is passed a
latitude and longitude from either the user's configuration or a requested
location.

It also supports returning values in the measurement system (Metric/Imperial)
provided, precluding us from having to do the conversions.

"""
import os
from mycroft.api import Api
from .weather import WeatherReport
from .ovosapiservice import OvosService
from json_database import JsonStorageXDG
import threading
import datetime as dt
import time

OPEN_WEATHER_MAP_LANGUAGES = (
    "af",
    "al",
    "ar",
    "bg",
    "ca",
    "cz",
    "da",
    "de",
    "el",
    "en",
    "es",
    "eu",
    "fa",
    "fi",
    "fr",
    "gl",
    "he",
    "hi",
    "hr",
    "hu",
    "id",
    "it",
    "ja",
    "kr",
    "la",
    "lt",
    "mk",
    "nl",
    "no",
    "pl",
    "pt",
    "pt_br",
    "ro",
    "ru",
    "se",
    "sk",
    "sl",
    "sp",
    "sr",
    "sv",
    "th",
    "tr",
    "ua",
    "uk",
    "vi",
    "zh_cn",
    "zh_tw",
    "zu"
)


class OpenWeatherMapApi(Api):
    """Use Open Weather Map's One Call API to retrieve weather information"""

    def __init__(self):
        super().__init__(path="owm")
        self.language = "en"
        self.localbackend = OvosService()
        self.cache_response_location = JsonStorageXDG(
            "skill-weather-response-cache")

    def get_weather_for_coordinates(
        self, measurement_system: str, latitude: float, longitude: float
    ) -> WeatherReport:
        """Issue an API call and map the return value into a weather report

        Args:
            measurement_system: Metric or Imperial measurement units
            latitude: the geologic latitude of the weather location
            longitude: the geologic longitude of the weather location
        """
        query_parameters = dict(
            exclude="minutely",
            lang=self.language,
            lat=latitude,
            lon=longitude,
            units=measurement_system
        )
        self.clear_cache_timer()
        if self.check_if_cached_weather_exist(latitude, longitude):
            cache_time = self.get_cached_weather_results(
                latitude, longitude)[0]
            response = self.get_cached_weather_results(latitude, longitude)[1]

            # add additional check for if the time is more than 15 minutes old and if so, refresh the cache
            if dt.datetime.now() - dt.datetime.fromtimestamp(cache_time) > dt.timedelta(minutes=15):
                try:
                    api_request = dict(path="/onecall", query=query_parameters)
                    response = self.request(api_request)
                    if response == {}:
                        response = self.localbackend.get_report_for_weather_onecall_type(
                            query=query_parameters)
                        weather_cache_response = {'time': time.mktime(dt.datetime.now(
                        ).timetuple()), 'lat': latitude, 'lon': longitude, 'response': response}
                        self.cache_weather_results(weather_cache_response)
                        local_weather = WeatherReport(response)
                    else:
                        weather_cache_response = {'time': time.mktime(dt.datetime.now(
                        ).timetuple()), 'lat': latitude, 'lon': longitude, 'response': response}
                        self.cache_weather_results(weather_cache_response)
                        local_weather = WeatherReport(response)
                except:
                    response = self.localbackend.get_report_for_weather_onecall_type(
                        query=query_parameters)
                    weather_cache_response = {'time': time.mktime(dt.datetime.now(
                    ).timetuple()), 'lat': latitude, 'lon': longitude, 'response': response}
                    self.cache_weather_results(weather_cache_response)
                    local_weather = WeatherReport(response)
            else:
                local_weather = WeatherReport(response)
        else:
            try:
                api_request = dict(path="/onecall", query=query_parameters)
                response = self.request(api_request)
                if response == {}:
                    response = self.localbackend.get_report_for_weather_onecall_type(
                        query=query_parameters)
                    weather_cache_response = {'time': time.mktime(dt.datetime.now(
                    ).timetuple()), 'lat': latitude, 'lon': longitude, 'response': response}
                    self.cache_weather_results(weather_cache_response)
                    local_weather = WeatherReport(response)
                else:
                    weather_cache_response = {'time': time.mktime(dt.datetime.now(
                    ).timetuple()), 'lat': latitude, 'lon': longitude, 'response': response}
                    self.cache_weather_results(weather_cache_response)
                    local_weather = WeatherReport(response)
            except:
                response = self.localbackend.get_report_for_weather_onecall_type(
                    query=query_parameters)
                weather_cache_response = {'time': time.mktime(dt.datetime.now(
                ).timetuple()), 'lat': latitude, 'lon': longitude, 'response': response}
                self.cache_weather_results(weather_cache_response)
                local_weather = WeatherReport(response)

        return local_weather

    def cache_weather_results(self, weather_response):
        cache_response = {'time': weather_response["time"], 'lat': weather_response["lat"],
                          'lon': weather_response["lon"], 'response': weather_response["response"]}
        if "caches" in self.cache_response_location:
            cache_responses = self.cache_response_location["caches"]
        else:
            cache_responses = []

        if cache_response not in cache_responses:
            cache_responses.append(cache_response)

        self.cache_response_location["caches"] = cache_responses
        self.cache_response_location.store()

    def check_if_cached_weather_exist(self, latitude, longitude):
        if "caches" in self.cache_response_location:
            cache_responses = self.cache_response_location["caches"]
            for cache_response in cache_responses:
                if cache_response["lat"] == latitude and cache_response["lon"] == longitude:
                    return True
                else:
                    return False
        else:
            return False

    def get_cached_weather_results(self, latitude, longitude):
        if "caches" in self.cache_response_location:
            cache_responses = self.cache_response_location["caches"]
            for cache_response in cache_responses:
                if cache_response["lat"] == latitude and cache_response["lon"] == longitude:
                    return [cache_response['time'], cache_response["response"]]

    def clear_cache_timer(self):
        if "caches" in self.cache_response_location:
            threading.Timer(900, self.clear_cache).start()

    def clear_cache(self):
        os.remove(self.cache_response_location.path)

    def set_language_parameter(self, language_config: str):
        """
        OWM supports 31 languages, see https://openweathermap.org/current#multi

        Convert Mycroft's language code to OpenWeatherMap's, if missing use english.

        Args:
            language_config: The Mycroft language code.
        """
        special_cases = {"cs": "cz", "ko": "kr", "lv": "la"}
        language_part_one, language_part_two = language_config.split('-')
        if language_config.replace('-', '_') in OPEN_WEATHER_MAP_LANGUAGES:
            self.language = language_config.replace('-', '_')
        elif language_part_one in OPEN_WEATHER_MAP_LANGUAGES:
            self.language = language_part_one
        elif language_part_two in OPEN_WEATHER_MAP_LANGUAGES:
            self.language = language_part_two
        elif language_part_one in special_cases:
            self.language = special_cases[language_part_one]
