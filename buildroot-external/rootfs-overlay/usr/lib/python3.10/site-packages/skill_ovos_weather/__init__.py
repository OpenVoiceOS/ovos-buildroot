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
"""Mycroft skill for communicating weather information

This skill uses the Open Weather Map One Call API to retrieve weather data
from around the globe (https://openweathermap.org/api/one-call-api).  It
proxies its calls to the API through Mycroft's officially supported API,
Selene.  The Selene API is also used to get geographical information about the
city name provided in the request.
"""
from datetime import datetime
from time import sleep
from typing import List, Tuple

from requests import HTTPError

from mycroft.skills import MycroftSkill, intent_handler, skill_api_method
from mycroft.skills.intent_services import AdaptIntent
from mycroft.messagebus.message import Message
from mycroft.util.parse import extract_number
from .skill import (
    CurrentDialog,
    DAILY,
    DailyDialog,
    DailyWeather,
    HOURLY,
    HourlyDialog,
    get_dialog_for_timeframe,
    LocationNotFoundError,
    OpenWeatherMapApi,
    WeatherConfig,
    WeatherIntent,
    WeatherReport,
    WeeklyDialog,
)

# TODO: VK Failures
#   Locations: Washington, D.C.
#
# TODO: Intent failures
#   Later weather: only the word "later" in the vocab file works all others
#       invoke datetime skill

TWELVE_HOUR = "half"


class WeatherSkill(MycroftSkill):
    """Main skill code for the weather skill."""

    def __init__(self):
        super().__init__("WeatherSkill")
        self.weather_api = None
        self.platform = None
        self.weather_config = None

    def initialize(self):
        """Do these things after the skill is loaded."""
        self.bus.on("skill-ovos-weather.openvoiceos.weather.request",
                    self.get_current_weather_homescreen)

        self.weather_api = OpenWeatherMapApi()
        self.weather_api.set_language_parameter(self.lang)
        self.platform = self.config_core["enclosure"].get("platform", "unknown")
        self.weather_config = WeatherConfig(self.config_core, self.settings)


    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .one_of("weather", "forecast")
        .optionally("location")
        .optionally("today")
    )
    def handle_current_weather(self, message: Message):
        """Handle current weather requests such as: what is the weather like?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_current_weather(message)

    @intent_handler(
        AdaptIntent()
        .require("query")
        .require("like")
        .require("outside")
        .optionally("location")
    )
    def handle_like_outside(self, message: Message):
        """Handle current weather requests such as: what's it like outside?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_current_weather(message)

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .one_of("weather", "forecast")
        .require("number-days")
        .optionally("location")
    )
    def handle_number_days_forecast(self, message: Message):
        """Handle multiple day forecast without specified location.

        Examples:
            "What is the 3 day forecast?"
            "What is the weather forecast?"

        Args:
            message: Message Bus event information from the intent parser
        """
        if self.voc_match(message.data["utterance"], "couple"):
            days = 2
        elif self.voc_match(message.data["utterance"], "few"):
            days = 3
        else:
            days = int(extract_number(message.data["utterance"]))
        self._report_multi_day_forecast(message, days)

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .one_of("weather", "forecast")
        .require("relative-day")
        .optionally("location")
    )
    def handle_one_day_forecast(self, message):
        """Handle forecast for a single day.

        Examples:
            "What is the weather forecast tomorrow?"
            "What is the weather forecast on Tuesday in Baltimore?"

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_one_day_forecast(message)

    @intent_handler(
        AdaptIntent()
        .require("query")
        .require("weather")
        .require("later")
        .optionally("location")
    )
    def handle_weather_later(self, message: Message):
        """Handle future weather requests such as: what's the weather later?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_one_hour_weather(message)

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .one_of("weather", "forecast")
        .require("relative-time")
        .optionally("relative-day")
        .optionally("location")
    )
    def handle_weather_at_time(self, message: Message):
        """Handle future weather requests such as: what's the weather tonight?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_one_hour_weather(message)

    @intent_handler(
        AdaptIntent()
        .require("query")
        .one_of("weather", "forecast")
        .require("weekend")
        .optionally("location")
    )
    def handle_weekend_forecast(self, message: Message):
        """Handle requests for the weekend forecast.

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weekend_forecast(message)

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .one_of("weather", "forecast")
        .require("week")
        .optionally("location")
    )
    def handle_week_weather(self, message: Message):
        """Handle weather for week (i.e. seven days).

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_week_summary(message)

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .require("temperature")
        .optionally("location")
        .optionally("unit")
        .optionally("today")
        .optionally("now")
    )
    def handle_current_temperature(self, message: Message):
        """Handle requests for current temperature.

        Examples:
            "What is the temperature in Celsius?"
            "What is the temperature in Baltimore now?"

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_temperature(message, temperature_type="current")

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .require("temperature")
        .require("relative-day")
        .optionally("location")
        .optionally("unit")
    )
    def handle_daily_temperature(self, message: Message):
        """Handle simple requests for current temperature.

        Examples: "What is the temperature?"

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_temperature(message, temperature_type="current")

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .require("temperature")
        .require("relative-time")
        .optionally("relative-day")
        .optionally("location")
    )
    def handle_hourly_temperature(self, message: Message):
        """Handle requests for current temperature at a relative time.

        Examples:
            "What is the temperature tonight?"
            "What is the temperature tomorrow morning?"

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_temperature(message)

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .require("high")
        .optionally("temperature")
        .optionally("location")
        .optionally("unit")
        .optionally("relative-day")
        .optionally("now")
        .optionally("today")
    )
    def handle_high_temperature(self, message: Message):
        """Handle a request for the high temperature.

        Examples:
            "What is the high temperature tomorrow?"
            "What is the high temperature in London on Tuesday?"

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_temperature(message, temperature_type="high")

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .require("low")
        .optionally("temperature")
        .optionally("location")
        .optionally("unit")
        .optionally("relative-day")
        .optionally("now")
        .optionally("today")
    )
    def handle_low_temperature(self, message: Message):
        """Handle a request for the high temperature.

        Examples:
            "What is the high temperature tomorrow?"
            "What is the high temperature in London on Tuesday?"

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_temperature(message, temperature_type="low")

    @intent_handler(
        AdaptIntent()
        .require("confirm-query-current")
        .one_of("hot", "cold")
        .optionally("location")
        .optionally("today")
    )
    def handle_is_it_hot(self, message: Message):
        """Handler for temperature requests such as: is it going to be hot today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_temperature(message, "current")

    @intent_handler(
        AdaptIntent()
        .optionally("query")
        .one_of("hot", "cold")
        .require("confirm-query")
        .optionally("location")
        .optionally("relative-day")
        .optionally("today")
    )
    def handle_how_hot_or_cold(self, message):
        """Handler for temperature requests such as: how cold will it be today?

        Args:
            message: Message Bus event information from the intent parser
        """
        utterance = message.data["utterance"]
        temperature_type = "high" if self.voc_match(utterance, "hot") else "low"
        self._report_temperature(message, temperature_type)

    @intent_handler(
        AdaptIntent()
        .require("confirm-query")
        .require("windy")
        .optionally("location")
        .optionally("relative-day")
    )
    def handle_is_it_windy(self, message: Message):
        """Handler for weather requests such as: is it windy today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_wind(message)

    @intent_handler(
        AdaptIntent()
        .require("how")
        .require("windy")
        .optionally("confirm-query")
        .optionally("relative-day")
        .optionally("location")
    )
    def handle_windy(self, message):
        """Handler for weather requests such as: how windy is it?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_wind(message)

    @intent_handler(
        AdaptIntent()
        .require("confirm-query")
        .require("snow")
        .optionally("location")
    )
    def handle_is_it_snowing(self, message: Message):
        """Handler for weather requests such as: is it snowing today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weather_condition(message, "snow")

    @intent_handler(
        AdaptIntent()
        .require("confirm-query")
        .require("clear")
        .optionally("location")
    )
    def handle_is_it_clear(self, message: Message):
        """Handler for weather requests such as: is the sky clear today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weather_condition(message, condition="clear")

    @intent_handler(
        AdaptIntent()
        .require("confirm-query")
        .require("clouds")
        .optionally("location")
        .optionally("relative-time")
    )
    def handle_is_it_cloudy(self, message: Message):
        """Handler for weather requests such as: is it cloudy today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weather_condition(message, "clouds")

    @intent_handler(
        AdaptIntent().require("ConfirmQuery").require("Fog").optionally("location")
    )
    def handle_is_it_foggy(self, message: Message):
        """Handler for weather requests such as: is it foggy today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weather_condition(message, "fog")

    @intent_handler(
        AdaptIntent().require("ConfirmQuery").require("Rain").optionally("location")
    )
    def handle_is_it_raining(self, message: Message):
        """Handler for weather requests such as: is it raining today?

        Args:
            message: Message Bus event information from the intent parser
0]       """
        self._report_weather_condition(message, "rain")

    @intent_handler("do-i-need-an-umbrella.intent")
    def handle_need_umbrella(self, message: Message):
        """Handler for weather requests such as: will I need an umbrella today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weather_condition(message, "rain")

    @intent_handler(
        AdaptIntent()
        .require("ConfirmQuery")
        .require("Thunderstorm")
        .optionally("Location")
    )
    def handle_is_it_storming(self, message: Message):
        """Handler for weather requests such as:  is it storming today?

        Args:
            message: Message Bus event information from the intent parser
        """
        self._report_weather_condition(message, "thunderstorm")

    @intent_handler(
        AdaptIntent()
        .require("When")
        .optionally("Next")
        .require("Precipitation")
        .optionally("Location")
    )
    def handle_next_precipitation(self, message: Message):
        """Handler for weather requests such as: when will it rain next?

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            forecast, timeframe = weather.get_next_precipitation(intent_data)
            intent_data.timeframe = timeframe
            dialog_args = intent_data, self.weather_config, forecast
            dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
            dialog.build_next_precipitation_dialog()
            spoken_percentage = self.translate(
                "percentage-number", data=dict(number=dialog.data["percent"])
            )
            dialog.data.update(percent=spoken_percentage)
            self._speak_weather(dialog)

    @intent_handler(
        AdaptIntent()
        .require("Query")
        .require("Humidity")
        .optionally("RelativeDay")
        .optionally("Location")
    )
    def handle_humidity(self, message: Message):
        """Handler for weather requests such as: how humid is it?

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            intent_weather = weather.get_weather_for_intent(intent_data)
            dialog_args = intent_data, self.weather_config, intent_weather
            dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
            dialog.build_humidity_dialog()
            dialog.data.update(
                humidity=self.translate(
                    "percentage-number", data=dict(num=dialog.data["humidity"])
                )
            )
            self._speak_weather(dialog)

    @intent_handler(
        AdaptIntent()
        .one_of("Query", "When")
        .optionally("Location")
        .require("Sunrise")
        .optionally("Today")
        .optionally("RelativeDay")
    )
    def handle_sunrise(self, message: Message):
        """Handler for weather requests such as: when is the sunrise?

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            intent_weather = weather.get_weather_for_intent(intent_data)
            dialog_args = intent_data, self.weather_config, intent_weather
            dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
            dialog.build_sunrise_dialog()
            weather_location = self._build_display_location(intent_data)
            self._display_sunrise_sunset(intent_weather, weather_location)
            self._speak_weather(dialog)

    @intent_handler(
        AdaptIntent()
        .one_of("Query", "When")
        .require("Sunset")
        .optionally("Location")
        .optionally("Today")
        .optionally("RelativeDay")
    )
    def handle_sunset(self, message: Message):
        """Handler for weather requests such as: when is the sunset?

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            intent_weather = weather.get_weather_for_intent(intent_data)
            dialog_args = intent_data, self.weather_config, intent_weather
            dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
            dialog.build_sunset_dialog()
            weather_location = self._build_display_location(intent_data)
            self._display_sunrise_sunset(intent_weather, weather_location)
            self._speak_weather(dialog)

    def _display_sunrise_sunset(self, forecast: DailyWeather, weather_location: str):
        """Display the sunrise and sunset.

        Args:
            forecast: daily forecasts to display
            weather_location: the geographical location of the weather
        """
        self.gui.clear()
        self.gui["weatherDate"] = forecast.date_time.strftime("%A %b %d")
        self.gui["weatherLocation"] = weather_location
        self.gui["sunrise"] = self._format_sunrise_sunset_time(forecast.sunrise)
        self.gui["sunset"] = self._format_sunrise_sunset_time(forecast.sunset)
        self.gui["ampm"] = self.config_core["time_format"] == TWELVE_HOUR
        self.gui.show_page("SunriseSunset.qml")

    def _format_sunrise_sunset_time(self, date_time: datetime) -> str:
        """Format a the sunrise or sunset datetime into a string for GUI display.

        The datetime builtin returns hour in two character format.  Remove the
        leading zero when present.

        Args:
            date_time: the sunrise or sunset

        Returns:
            the value to display on the screen
        """
        if self.config_core["time_format"] == TWELVE_HOUR:
            display_time = date_time.strftime("%I:%M")
            if display_time.startswith("0"):
                display_time = display_time[1:]
        else:
            display_time = date_time.strftime("%H:%M")

        return display_time

    def _report_current_weather(self, message: Message):
        """Handles all requests for current weather conditions.

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            weather_location = self._build_display_location(intent_data)
            self._display_current_conditions(weather, weather_location)
            dialog = CurrentDialog(intent_data, self.weather_config, weather.current)
            dialog.build_weather_dialog()
            self._speak_weather(dialog)
            dialog = CurrentDialog(intent_data, self.weather_config, weather.current)
            dialog.build_high_low_temperature_dialog()
            self._speak_weather(dialog)
            if self.gui.connected:
                sleep(5)
                self._display_hourly_forecast(weather, weather_location)
                sleep(5)
                four_day_forecast = weather.daily[1:5]
                self._display_multi_day_forecast(four_day_forecast, intent_data)

    def _display_current_conditions(
        self, weather: WeatherReport, weather_location: str
    ):
        """Display current weather conditions on a screen.

        This is the first screen that shows.  Others will follow.

        Args:
            weather: current weather conditions from Open Weather Maps
            weather_location: the geographical location of the reported weather
        """
        if self.gui.connected:
            page_name = "CurrentWeather.qml"
            self.log.info(weather.current.date_time.now().strftime("%a %B %d, %Y"))
            self.gui["weatherCode"] = weather.current.condition.ovos_code
            self.gui["currentTimezone"] = weather.current.date_time.now().strftime("%a %B %d, %Y")
            self.gui["currentTemperature"] = weather.current.temperature
            self.gui["weatherCondition"] = weather.current.condition.image
            self.gui["weatherLocation"] = weather_location
            self.gui["highTemperature"] = weather.current.high_temperature
            self.gui["lowTemperature"] = weather.current.low_temperature
            self.gui["windSpeed"] = weather.current.wind_speed
            self.gui["humidity"] = weather.current.humidity
            self.gui.show_page(page_name)
        else:
            self.enclosure.deactivate_mouth_events()
            self.enclosure.weather_display(
                weather.current.condition.code, weather.current.temperature
            )

    def _build_display_location(self, intent_data: WeatherIntent) -> str:
        """Build a string representing the location of the weather for display on GUI

        The return value will be the device's configured location if no location is
        specified in the intent.  If a location is specified, and it is in the same
        country as that in the device configuration, the return value will be city and
        region.  A specified location in a different country will result in a return
        value of city and country.

        Args:
            intent_data: information about the intent that was triggered

        Returns:
            The weather location to be displayed on the GUI
        """
        if intent_data.geolocation:
            location = [intent_data.geolocation["city"]]
            if intent_data.geolocation["country"] == self.weather_config.country:
                location.append(intent_data.geolocation["region"])
            else:
                location.append(intent_data.geolocation["country"])
        else:
            location = [self.weather_config.city, self.weather_config.state]

        return ", ".join(location)

    def _report_one_hour_weather(self, message: Message):
        """Handles requests for a one hour forecast.

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            try:
                forecast = weather.get_forecast_for_hour(intent_data)
            except IndexError:
                self.speak_dialog("forty-eight.hours.available")
            else:
                dialog = HourlyDialog(intent_data, self.weather_config, forecast)
                dialog.build_weather_dialog()
                self._speak_weather(dialog)

    def _display_hourly_forecast(self, weather: WeatherReport, weather_location: str):
        """Display hourly forecast on a device that supports the GUI.

        On the Mark II this screen is the final for current weather.  It can
        also be shown when the hourly forecast is requested.

        :param weather: hourly weather conditions from Open Weather Maps
        """
        hourly_forecast = []
        for hour_count, hourly in enumerate(weather.hourly):
            if not hour_count:
                continue
            if hour_count > 4:
                break
            if self.config_core["time_format"] == TWELVE_HOUR:
                # The datetime builtin returns hour in two character format.  Convert
                # to a integer and back again to remove the leading zero when present.
                hour = int(hourly.date_time.strftime("%I"))
                am_pm = hourly.date_time.strftime(" %p")
                formatted_time = str(hour) + am_pm
            else:
                formatted_time = hourly.date_time.strftime("%H:00")
            hourly_forecast.append(
                dict(
                    time=hourly.date_time.strftime(formatted_time),
                    precipitation=hourly.chance_of_precipitation,
                    temperature=hourly.temperature,
                    weatherCondition=hourly.condition.ovos_code,
                )
            )
        self.gui["weatherCode"] = weather.current.condition.ovos_code
        self.gui["weatherLocation"] = weather_location
        self.gui["hourlyForecast"] = dict(hours=hourly_forecast)
        self.gui.show_page("HourlyForecast.qml")

    def _report_one_day_forecast(self, message: Message):
        """Handles all requests for a single day forecast.

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = WeatherIntent(message, self.lang)
        weather = self._get_weather(intent_data)
        if weather is not None:
            forecast = weather.get_forecast_for_date(intent_data)
            dialogs = self._build_forecast_dialogs([forecast], intent_data)
            if self.gui.connected:
                self._display_one_day(forecast, intent_data)
            for dialog in dialogs:
                self._speak_weather(dialog)

    def _display_one_day(
        self, forecast: DailyWeather, intent_data: WeatherIntent
    ):
        """Display the forecast for a single day on a Mark II.

        :param forecast: daily forecasts to display
        """
        self.gui.clear()
        self.gui["weatherLocation"] = self._build_display_location(intent_data)
        self.gui["weatherCondition"] = forecast.condition.ovos_code
        self.gui["weatherDate"] = forecast.date_time.strftime("%a %B %d, %Y")
        self.gui["highTemperature"] = forecast.temperature.high
        self.gui["lowTemperature"] = forecast.temperature.low
        self.gui["chanceOfPrecipitation"] = str(forecast.chance_of_precipitation)
        self.gui.show_page("SingleDay.qml")

    def _report_multi_day_forecast(self, message: Message, days: int):
        """Handles all requests for multiple day forecasts.

        :param message: Message Bus event information from the intent parser
        """
        intent_data = WeatherIntent(message, self.lang)
        weather = self._get_weather(intent_data)
        if weather is not None:
            try:
                forecast = weather.get_forecast_for_multiple_days(days)
            except IndexError:
                self.speak_dialog("seven.days.available")
                forecast = weather.get_forecast_for_multiple_days(7)
            dialogs = self._build_forecast_dialogs(forecast, intent_data)
            self._display_multi_day_forecast(forecast, intent_data)
            for dialog in dialogs:
                self._speak_weather(dialog)

    def _report_weekend_forecast(self, message: Message):
        """Handles requests for a weekend forecast.

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            forecast = weather.get_weekend_forecast()
            dialogs = self._build_forecast_dialogs(forecast, intent_data)
            self._display_multi_day_forecast(forecast, intent_data)
            for dialog in dialogs:
                self._speak_weather(dialog)

    def _build_forecast_dialogs(
        self, forecast: List[DailyWeather], intent_data: WeatherIntent
    ) -> List[DailyDialog]:
        """
        Build the dialogs for each of the forecast days being reported to the user.

        :param forecast: daily forecasts to report
        :param intent_data: information about the intent that was triggered
        :return: one DailyDialog instance for each day being reported.
        """
        dialogs = list()
        for forecast_day in forecast:
            dialog = DailyDialog(intent_data, self.weather_config, forecast_day)
            dialog.build_weather_dialog()
            dialogs.append(dialog)

        return dialogs

    def _report_week_summary(self, message: Message):
        """Summarize the week's weather rather than giving daily details.

        When the user requests the weather for the week, rather than give a daily
        forecast for seven days, summarize the weather conditions for the week.

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = WeatherIntent(message, self.lang)
        weather = self._get_weather(intent_data)
        if weather is not None:
            forecast = weather.get_forecast_for_multiple_days(7)
            dialogs = self._build_weekly_condition_dialogs(forecast, intent_data)
            dialogs.append(self._build_weekly_temperature_dialog(forecast, intent_data))
            self._display_multi_day_forecast(forecast, intent_data)
            for dialog in dialogs:
                self._speak_weather(dialog)

    def _build_weekly_condition_dialogs(
        self, forecast: List[DailyWeather], intent_data: WeatherIntent
    ) -> List[WeeklyDialog]:
        """Build the dialog communicating a weather condition on days it is forecasted.

        Args:
            forecast: seven day daily forecast
            intent_data: Parsed intent data

        Returns:
            List of dialogs for each condition expected in the coming week.
        """
        dialogs = list()
        conditions = set([daily.condition.category for daily in forecast])
        for condition in conditions:
            dialog = WeeklyDialog(intent_data, self.weather_config, forecast)
            dialog.build_condition_dialog(condition=condition)
            dialogs.append(dialog)

        return dialogs

    def _build_weekly_temperature_dialog(
        self, forecast: List[DailyWeather], intent_data: WeatherIntent
    ) -> WeeklyDialog:
        """Build the dialog communicating the forecasted range of temperatures.

        Args:
            forecast: seven day daily forecast
            intent_data: Parsed intent data

        Returns:
            Dialog for the temperature ranges over the coming week.
        """
        dialog = WeeklyDialog(intent_data, self.weather_config, forecast)
        dialog.build_temperature_dialog()

        return dialog

    def _display_multi_day_forecast(
        self, forecast: List[DailyWeather], intent_data: WeatherIntent
    ):
        """Display daily forecast data on devices that support the GUI.

        Args:
            forecast: daily forecasts to display
            intent_data: Parsed intent data
        """
        self._display_multi_day_scalable(forecast)

    def _display_multi_day_scalable(self, forecast: List[DailyWeather]):
        """Display daily forecast data on GUI devices other than the Mark II.

        The generic layout supports displaying two days of a forecast at a time.

        Args:
            forecast: daily forecasts to display
        """
        display_data = []
        for day_number, day in enumerate(forecast):
            if day_number == 4:
                break
            display_data.append(
                dict(
                    weatherCondition=day.condition.ovos_code,
                    highTemperature=day.temperature.high,
                    lowTemperature=day.temperature.low,
                    date=day.date_time.strftime("%a"),
                )
            )
        self.gui["forecast"] = dict(all=display_data)
        self.gui.show_page("DailyForecast.qml")

    def _report_temperature(self, message: Message, temperature_type: str = None):
        """Handles all requests for a temperature.

        Args:
            message: Message Bus event information from the intent parser
            temperature_type: current, high or low temperature
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            intent_weather = weather.get_weather_for_intent(intent_data)
            dialog_args = intent_data, self.weather_config, intent_weather
            dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
            dialog.build_temperature_dialog(temperature_type)
            self._speak_weather(dialog)

    def _report_weather_condition(self, message: Message, condition: str):
        """Handles all requests for a specific weather condition.

        Args:
            message: Message Bus event information from the intent parser
            condition: the weather condition specified by the user
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            intent_weather = weather.get_weather_for_intent(intent_data)
            dialog = self._build_condition_dialog(
                intent_weather, intent_data, condition
            )
            self._speak_weather(dialog)

    def _build_condition_dialog(
        self, weather, intent_data: WeatherIntent, condition: str
    ):
        """Builds a dialog for the requested weather condition.

        Args:
            weather: Current, hourly or daily weather forecast
            intent_data: Parsed intent data
            condition: weather condition requested by the user
        """
        dialog_args = intent_data, self.weather_config, weather
        dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
        intent_match = self.voc_match(weather.condition.category.lower(), condition)
        dialog.build_condition_dialog(intent_match)
        dialog.data.update(condition=self.translate(weather.condition.description))

        return dialog

    def _report_wind(self, message: Message):
        """Handles all requests for a wind conditions.

        Args:
            message: Message Bus event information from the intent parser
        """
        intent_data = self._get_intent_data(message)
        weather = self._get_weather(intent_data)
        if weather is not None:
            intent_weather = weather.get_weather_for_intent(intent_data)
            intent_weather.wind_direction = self.translate(
                intent_weather.wind_direction
            )
            dialog_args = intent_data, self.weather_config, intent_weather
            dialog = get_dialog_for_timeframe(intent_data.timeframe, dialog_args)
            dialog.build_wind_dialog()
            self._speak_weather(dialog)

    def _get_intent_data(self, message: Message) -> WeatherIntent:
        """Parse the intent data from the message into data used in the skill.

        Args:
            message: Message Bus event information from the intent parser

        Returns:
            parsed information about the intent
        """
        intent_data = None
        try:
            intent_data = WeatherIntent(message, self.lang)
        except ValueError:
            self.speak_dialog("cant.get.forecast")
        else:
            if self.voc_match(intent_data.utterance, "relative-time"):
                intent_data.timeframe = HOURLY
            elif self.voc_match(intent_data.utterance, "later"):
                intent_data.timeframe = HOURLY
            elif self.voc_match(intent_data.utterance, "relative-day"):
                if not self.voc_match(intent_data.utterance, "today"):
                    intent_data.timeframe = DAILY

        return intent_data

    def _get_weather(self, intent_data: WeatherIntent) -> WeatherReport:
        """Call the Open Weather Map One Call API to get weather information

        Args:
            intent_data: Parsed intent data

        Returns:
            An object representing the data returned by the API
        """
        weather = None
        if intent_data is not None:
            try:
                latitude, longitude = self._determine_weather_location(intent_data)
                weather = self.weather_api.get_weather_for_coordinates(
                    self.config_core.get("system_unit"), latitude, longitude
                )
            except HTTPError as api_error:
                self.log.exception("Weather API failure")
                self._handle_api_error(api_error)
            except LocationNotFoundError:
                self.log.exception("City not found.")
                self.speak_dialog(
                    "location-not-found", data=dict(location=intent_data.location)
                )
            except Exception:
                self.log.exception("Unexpected error retrieving weather")
                self.speak_dialog("cant-get-forecast")

        return weather

    def _handle_api_error(self, exception: HTTPError):
        """Communicate an error condition to the user.

        Args:
            exception: the HTTPError returned by the API call
        """
        if exception.response.status_code == 401:
            self.bus.emit(Message("mycroft.not.paired"))
        else:
            self.speak_dialog("cant.get.forecast")

    def _determine_weather_location(
        self, intent_data: WeatherIntent
    ) -> Tuple[float, float]:
        """Determine latitude and longitude using the location data in the intent.

        Args:
            intent_data: Parsed intent data

        Returns
            latitude and longitude of the location
        """
        if intent_data.location is None:
            latitude = self.weather_config.latitude
            longitude = self.weather_config.longitude
        else:
            latitude = intent_data.geolocation["latitude"]
            longitude = intent_data.geolocation["longitude"]

        return latitude, longitude

    def _speak_weather(self, dialog):
        """Instruct device to speak the contents of the specified dialog.

        :param dialog: the dialog that will be spoken
        """
        self.log.info("Speaking dialog: " + dialog.name)
        self.speak_dialog(dialog.name, dialog.data, wait=True)

    @skill_api_method
    def get_current_weather_homescreen(self, message=None):
        """Get the current temperature and weather condition.
        Returns:
            Dict: {
                weather_temp: current temperature
                high_temperature: forecasted high for today
                low_temperature: forecasted low for today
                weather_code: code representing overall weather condition
                                see Maps for all codes in skill/weather.py
                condition_category: category of conditions eg "Cloudy"
                condition_description: more detail eg "slightly cloudly"
                system_unit: whether the report uses metric or imperial
            }
        """
        system_unit = self.config_core.get("system_unit")
        try:
            weather = self.weather_api.get_weather_for_coordinates(
                system_unit,
                self.weather_config.latitude,
                self.weather_config.longitude
            )

            result = dict(
                weather_temp=weather.current.temperature,
                high_temperature=weather.current.high_temperature,
                low_temperature=weather.current.low_temperature,
                weather_code=weather.current.condition.code,
                condition_category=weather.current.condition.category,
                condition_description=weather.current.condition.description,
                system_unit=system_unit
            )

            self.bus.emit(Message("skill-ovos-weather.openvoiceos.weather.response",
                                  {"report": result}))
            return result
        except Exception:
            self.log.exception("Unexpected error getting weather for skill API.")

    def stop(self):
        self.gui.release()

def create_skill():
    """Boilerplate to invoke the weather skill."""
    return WeatherSkill()
