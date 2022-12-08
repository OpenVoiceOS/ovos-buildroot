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
"""Abstraction of dialog building for the weather skill.

There are A LOT of dialog files in this skill.  All the permutations of timeframe,
weather condition and location add up fast.  To help with discoverability, a naming
convention was applied to the dialog files:
    <timeframe>-<weather info>-<qualifier>-<locale>.dialog

    Example:
         daily-temperature-high-local.dialog

    * Timeframe: the date or time applicable to the forecast.  This skill supports
        current, hourly and daily weather.
    * Weather info: a description of what type of weather the dialog refers to.
        Examples include "temperature", "weather" and "sunrise".
    * Qualifier: further qualifies what type of weather is being reported.  For
        example, temperature can be qualified by "high" or "low".
    * Locale: indicates if the dialog is for local weather or weather in a remote
        location.

The skill class will use the "name" and "data" attributes to pass to the TTS process.
"""
from typing import List, Tuple

from mycroft.util.format import join_list, nice_number, nice_time
from mycroft.util.time import now_local
from .config import WeatherConfig
from .intent import WeatherIntent
from .util import get_speakable_day_of_week, get_time_period
from .weather import (
    CURRENT,
    CurrentWeather,
    DAILY,
    DailyWeather,
    HOURLY,
    HourlyWeather,
)

# TODO: MISSING DIALOGS
#   - current.clear.alternative.local
#   - current.clouds.alternative.local
#   - daily.snow.alternative.local
#   - all hourly.<condition>.alternative.local/location
#   - all hourly.<condition>.not.expected.local/location
class WeatherDialog:
    """Abstract base class for the weather dialog builders."""

    def __init__(self, intent_data: WeatherIntent, config: WeatherConfig):
        self.intent_data = intent_data
        self.config = config
        self.name = None
        self.data = None

    def _add_location(self):
        """Add location information to the dialog."""
        if self.intent_data.location is None:
            self.name += "-local"
        else:
            self.name += "-location"
            if self.config.country == self.intent_data.geolocation["country"]:
                spoken_location = ", ".join(
                    [
                        self.intent_data.geolocation["city"],
                        self.intent_data.geolocation["region"],
                    ]
                )
            else:
                spoken_location = ", ".join(
                    [
                        self.intent_data.geolocation["city"],
                        self.intent_data.geolocation["country"],
                    ]
                )
            self.data.update(location=spoken_location)


class CurrentDialog(WeatherDialog):
    """Weather dialog builder for current weather."""

    def __init__(
        self, intent_data: WeatherIntent, config: WeatherConfig, weather: CurrentWeather
    ):
        super().__init__(intent_data, config)
        self.weather = weather
        self.name = CURRENT

    def build_weather_dialog(self):
        """Build the components necessary to speak current weather."""
        self.name += "-weather"
        self.data = dict(
            condition=self.weather.condition.description,
            temperature=self.weather.temperature,
            temperature_unit=self.config.temperature_unit,
        )
        self._add_location()

    def build_high_low_temperature_dialog(self):
        """Build the components necessary to speak high and low temperature."""
        self.name += "-temperature-high-low"
        self.data = dict(
            high_temperature=self.weather.high_temperature,
            low_temperature=self.weather.low_temperature,
        )

    def build_temperature_dialog(self, temperature_type: str):
        """Build the components necessary to speak the current temperature.

        :param temperature_type: indicates if temperature is current, high or low
        """
        self.name += "-temperature"
        if temperature_type == "high":
            self.name += "-high"
            self.data = dict(temperature=self.weather.high_temperature)
        elif temperature_type == "low":
            self.name += "-low"
            self.data = dict(temperature=self.weather.low_temperature)
        else:
            self.data = dict(temperature=self.weather.temperature)
        self.data.update(
            temperature_unit=self.intent_data.unit or self.config.temperature_unit
        )
        self._add_location()

    def build_condition_dialog(self, intent_match: bool):
        """Select the relevant dialog file for condition based reports.

        A condition can for example be "snow" or "rain".

        :param intent_match: true if intent matches a vocabulary for the condition
        """
        self.data = dict(condition=self.weather.condition.description.lower())
        if intent_match:
            self.name += "-condition-expected"
        else:
            self.name += "-condition-not-expected".format(
                self.weather.condition.category.lower()
            )
        self._add_location()

    def build_sunrise_dialog(self):
        """Build the components necessary to speak the sunrise time."""
        if self.intent_data.location is None:
            now = now_local()
        else:
            now = now_local(tz=self.intent_data.geolocation["timezone"])
        if now < self.weather.sunrise:
            self.name += "-sunrise-future"
        else:
            self.name += "-sunrise-past"
        self.data = dict(time=nice_time(self.weather.sunrise))
        self._add_location()

    def build_sunset_dialog(self):
        """Build the components necessary to speak the sunset time."""
        if self.intent_data.location is None:
            now = now_local()
        else:
            now = now_local(tz=self.intent_data.geolocation["timezone"])
        if now < self.weather.sunset:
            self.name += ".sunset.future"
        else:
            self.name = ".sunset.past"
        self.data = dict(time=nice_time(self.weather.sunset))
        self._add_location()

    def build_wind_dialog(self):
        """Build the components necessary to speak the wind conditions."""
        wind_strength = self.weather.determine_wind_strength(self.config.speed_unit)
        self.data = dict(
            speed=nice_number(self.weather.wind_speed),
            speed_unit=self.config.speed_unit,
            direction=self.weather.wind_direction,
        )
        self.name += "-wind-" + wind_strength
        self._add_location()

    def build_humidity_dialog(self):
        """Build the components necessary to speak the percentage humidity."""
        self.data = dict(percent=self.weather.humidity)
        self.name += "-humidity"
        self._add_location()


class HourlyDialog(WeatherDialog):
    """Weather dialog builder for hourly weather."""

    def __init__(
        self, intent_data: WeatherIntent, config: WeatherConfig, weather: HourlyWeather
    ):
        super().__init__(intent_data, config)
        self.weather = weather
        self.name = HOURLY

    def build_weather_dialog(self):
        """Build the components necessary to speak the forecast for a hour."""
        self.name += "-weather"
        self.data = dict(
            condition=self.weather.condition.description,
            time=self.weather.date_time.strftime("%H:00"),
            temperature=self.weather.temperature,
        )
        self._add_location()

    def build_temperature_dialog(self, _):
        """Build the components necessary to speak the hourly temperature."""
        self.name += "-temperature"
        self.data = dict(
            temperature=self.weather.temperature,
            time=get_time_period(self.weather.date_time),
            temperature_unit=self.intent_data.unit or self.config.temperature_unit,
        )
        self._add_location()

    def build_condition_dialog(self, intent_match: bool):
        """Select the relevant dialog file for condition based reports.

        A condition can for example be "snow" or "rain".

        :param intent_match: true if intent matches a vocabulary for the condition
        """
        self.data = dict(
            condition=self.weather.condition.description.lower(),
            time=nice_time(self.weather.date_time),
        )
        if intent_match:
            self.name += "-condition-expected"
        else:
            self.name += "-condition-not-expected".format(
                self.weather.condition.category.lower()
            )
        self._add_location()

    def build_wind_dialog(self):
        """Build the components necessary to speak the wind conditions."""
        wind_strength = self.weather.determine_wind_strength(self.config.speed_unit)
        self.data = dict(
            speed=nice_number(self.weather.wind_speed),
            speed_unit=self.config.speed_unit,
            direction=self.weather.wind_direction,
            time=nice_time(self.weather.date_time),
        )
        self.name += "-wind-" + wind_strength
        self._add_location()

    def build_next_precipitation_dialog(self):
        """Build the components necessary to speak the next chance of rain."""
        if self.weather is None:
            self.name += "-precipitation-next-none"
            self.data = dict()
        else:
            self.name += "-precipitation-next"
            self.data = dict(
                percent=self.weather.chance_of_precipitation,
                precipitation="rain",
                day=get_speakable_day_of_week(self.weather.date_time),
                time=get_time_period(self.weather.date_time),
            )
        self._add_location()


class DailyDialog(WeatherDialog):
    """Weather dialog builder for daily weather."""

    def __init__(
        self, intent_data: WeatherIntent, config: WeatherConfig, weather: DailyWeather
    ):
        super().__init__(intent_data, config)
        self.weather = weather
        self.name = DAILY

    def build_weather_dialog(self):
        """Build the components necessary to speak the forecast for a day."""
        self.name += "-weather"
        self.data = dict(
            condition=self.weather.condition.description,
            day=get_speakable_day_of_week(self.weather.date_time),
            high_temperature=self.weather.temperature.high,
            low_temperature=self.weather.temperature.low,
        )
        self._add_location()

    def build_temperature_dialog(self, temperature_type: str):
        """Build the components necessary to speak the daily temperature.

        :param temperature_type: indicates if temperature is day, high or low
        """
        self.name += "-temperature"
        if temperature_type == "high":
            self.name += "-high"
            self.data = dict(temperature=self.weather.temperature.high)
        elif temperature_type == "low":
            self.name += "-low"
            self.data = dict(temperature=self.weather.temperature.low)
        else:
            self.data = dict(temperature=self.weather.temperature.day)
        self.data.update(
            day=get_speakable_day_of_week(self.weather.date_time),
            temperature_unit=self.intent_data.unit or self.config.temperature_unit,
        )
        self._add_location()

    def build_condition_dialog(self, intent_match: bool):
        """Select the relevant dialog file for condition based reports.

        A condition can for example be "snow" or "rain".

        :param intent_match: true if intent matches a vocabulary for the condition
        """
        self.data = dict(
            condition=self.weather.condition.description.lower(),
            day=get_speakable_day_of_week(self.weather.date_time),
        )
        if intent_match:
            self.name += "-condition-expected"
        else:
            self.name += "-condition-not-expected".format(
                self.weather.condition.category.lower()
            )
        self._add_location()

    def build_sunrise_dialog(self):
        """Build the components necessary to speak the sunrise time."""
        self.name += "-sunrise"
        self.data = dict(time=nice_time(self.weather.sunrise))
        self.data.update(day=get_speakable_day_of_week(self.weather.date_time))
        self._add_location()

    def build_sunset_dialog(self):
        """Build the components necessary to speak the sunset time."""
        self.name += "-sunset"
        self.data = dict(time=nice_time(self.weather.sunset))
        self.data.update(day=get_speakable_day_of_week(self.weather.date_time))
        self._add_location()

    def build_wind_dialog(self):
        """Build the components necessary to speak the wind conditions."""
        wind_strength = self.weather.determine_wind_strength(self.config.speed_unit)
        self.data = dict(
            day=get_speakable_day_of_week(self.weather.date_time),
            speed=nice_number(self.weather.wind_speed),
            speed_unit=self.config.speed_unit,
            direction=self.weather.wind_direction,
        )
        self.name += "-wind-" + wind_strength
        self._add_location()

    def build_humidity_dialog(self):
        """Build the components necessary to speak the percentage humidity."""
        self.data = dict(
            percent=self.weather.humidity, day=get_speakable_day_of_week(self.weather.date_time)
        )
        self.name += "-humidity"
        self._add_location()

    def build_next_precipitation_dialog(self):
        """Build the components necessary to speak the next chance of rain."""
        if self.weather is None:
            self.name += "-precipitation-next-none"
            self.data = dict()
        else:
            self.name += "-precipitation-next"
            self.data = dict(
                percent=self.weather.chance_of_precipitation,
                precipitation="rain",
                day=get_speakable_day_of_week(self.weather.date_time),
            )
        self._add_location()


class WeeklyDialog(WeatherDialog):
    """Weather dialog builder for weekly weather."""

    def __init__(
        self,
        intent_data: WeatherIntent,
        config: WeatherConfig,
        forecast: List[DailyWeather],
    ):
        super().__init__(intent_data, config)
        self.forecast = forecast
        self.name = "weekly"

    def build_temperature_dialog(self):
        """Build the components necessary to temperature ranges for a week."""
        low_temperatures = [daily.temperature.low for daily in self.forecast]
        high_temperatures = [daily.temperature.high for daily in self.forecast]
        self.name += "-temperature"
        self.data = dict(
            low_min=min(low_temperatures),
            low_max=max(low_temperatures),
            high_min=min(high_temperatures),
            high_max=max(high_temperatures),
        )

    def build_condition_dialog(self, condition: str):
        """Build the components necessary to speak the days of week for a condition."""
        self.name += "-condition"
        self.data = dict(condition=condition)
        days_with_condition = []
        for daily in self.forecast:
            if daily.condition.category == condition:
                day = get_speakable_day_of_week(daily.date_time)
                days_with_condition.append(day)
        self.data.update(days=join_list(days_with_condition, "and"))


def get_dialog_for_timeframe(timeframe: str, dialog_ags: Tuple):
    """Use the intent data to determine which dialog builder to use.

    :param timeframe: current, hourly, daily
    :param dialog_ags: Arguments to pass to the dialog builder
    :return: The correct dialog builder for the timeframe
    """
    if timeframe == DAILY:
        dialog = DailyDialog(*dialog_ags)
    elif timeframe == HOURLY:
        dialog = HourlyDialog(*dialog_ags)
    else:
        dialog = CurrentDialog(*dialog_ags)

    return dialog
