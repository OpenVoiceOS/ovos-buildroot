# Copyright 2017, Mycroft AI Inc.
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

import datetime
import json
import pytz
import re
import time
from pathlib import Path
from timezonefinder import TimezoneFinder
import geocoder

import mycroft.audio
from adapt.intent import IntentBuilder
from mycroft.util.format import (nice_date, nice_duration, nice_time,
                                 date_time_format)
from mycroft.messagebus.message import Message
from mycroft import MycroftSkill, intent_handler
from mycroft.skills import skill_api_method
from mycroft.util.parse import (extract_datetime, fuzzy_match, extract_number,
                                normalize)
from mycroft.util.time import now_utc, to_local, now_local


def speakable_timezone(tz):
    """Convert timezone to a better speakable version

    Splits joined words,  e.g. EasterIsland  to "Easter Island",
    "North_Dakota" to "North Dakota" etc.
    Then parses the output into the correct order for speech,
    eg. "America/North Dakota/Center" to
    resulting in something like  "Center North Dakota America", or
    "Easter Island Chile"
    """
    say = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", tz)
    say = say.replace("_", " ")
    say = say.split("/")
    say.reverse()
    return " ".join(say)


class TimeSkill(MycroftSkill):

    def __init__(self):
        super(TimeSkill, self).__init__("TimeSkill")
        self.displayed_time = None
        self.display_tz = None
        self.answering_query = False
        self.default_timezone = None

    def initialize(self):
        date_time_format.cache(self.lang)

        # Start a callback that repeats every 10 seconds
        # TODO: Add mechanism to only start timer when UI setting
        #       is checked, but this requires a notifier for settings
        #       updates from the web.
        now = datetime.datetime.now()
        callback_time = (datetime.datetime(now.year, now.month, now.day,
                                           now.hour, now.minute) +
                         datetime.timedelta(seconds=60))
        self.schedule_repeating_event(self.update_display, callback_time, 10)

    # TODO:19.08 Moved to MycroftSkill
    @property
    def platform(self):
        """ Get the platform identifier string

        Returns:
            str: Platform identifier, such as "mycroft_mark_1",
                 "mycroft_picroft", "mycroft_mark_2".  None for nonstandard.
        """
        if self.config_core and self.config_core.get("enclosure"):
            return self.config_core["enclosure"].get("platform")
        else:
            return None

    @property
    def build_info(self):
        """The /etc/mycroft/build-info.json file as a Dict."""
        data = {}
        filename = "/etc/mycroft/build-info.json"
        if (self.config_core["enclosure"].get("development_device")
            and Path(filename).is_file()):
            with open(filename, 'r') as build_info:
                data = json.loads(build_info.read())
        return data

    @property
    def use_24hour(self):
        return self.config_core.get('time_format') == 'full'

    def _get_timezone_from_builtins(self, locale):
        if "/" not in locale:
            try:
                # This handles common city names, like "Dallas" or "Paris"
                # first get the lat / long.
                g = geocoder.osm(locale)

                # now look it up
                tf = TimezoneFinder()
                timezone = tf.timezone_at(lng=g.lng, lat=g.lat)
                return pytz.timezone(timezone)
            except Exception:
                pass

        try:
            # This handles codes like "America/Los_Angeles"
            return pytz.timezone(locale)
        except Exception:
            pass
        return None

    def _get_timezone_from_table(self, locale):
        """Check lookup table for timezones.

        This can also be a translation layer.
        E.g. "china = GMT+8"
        """
        timezones = self.translate_namedvalues("timezone.value")
        for timezone in timezones:
            if locale.lower() == timezone.lower():
                # assumes translation is correct
                return pytz.timezone(timezones[timezone].strip())
        return None

    def _get_timezone_from_fuzzymatch(self, locale):
        """Fuzzymatch a location against the pytz timezones.

        The pytz timezones consists of
        Location/Name pairs.  For example:
            ["Africa/Abidjan", "Africa/Accra", ... "America/Denver", ...
             "America/New_York", ..., "America/North_Dakota/Center", ...
             "Cuba", ..., "EST", ..., "Egypt", ..., "Etc/GMT+3", ...
             "Etc/Zulu", ... "US/Eastern", ... "UTC", ..., "Zulu"]

        These are parsed and compared against the provided location.
        """
        target = locale.lower()
        best = None
        for name in pytz.all_timezones:
            # Separate at '/'
            normalized = name.lower().replace("_", " ").split("/")
            if len(normalized) == 1:
                pct = fuzzy_match(normalized[0], target)
            elif len(normalized) >= 2:
                # Check for locations like "Sydney"
                pct1 = fuzzy_match(normalized[1], target)
                # locations like "Sydney Australia" or "Center North Dakota"
                pct2 = fuzzy_match(normalized[-2] + " " + normalized[-1],
                                   target)
                pct3 = fuzzy_match(normalized[-1] + " " + normalized[-2],
                                   target)
                pct = max(pct1, pct2, pct3)
            if not best or pct >= best[0]:
                best = (pct, name)
        if best and best[0] > 0.8:
            # solid choice
            return pytz.timezone(best[1])
        elif best and best[0] > 0.3:
            say = speakable_timezone(best[1])
            if self.ask_yesno("did.you.mean.timezone",
                              data={"zone_name": say}) == "yes":
                return pytz.timezone(best[1])
        else:
            return None

    def get_timezone(self, locale):
        """Get the timezone.

        This uses a variety of approaches to determine the intended timezone.
        If locale is the user defined locale, we save that timezone and cache it.
        """

        # default timezone exists, so return it.
        if str(self.default_timezone) == locale == self.location_timezone:
            return self.default_timezone

        # no default timezone has either been requested or saved
        timezone = self._get_timezone_from_builtins(locale)
        if not timezone:
            timezone = self._get_timezone_from_table(locale)
        if not timezone:
            timezone = self._get_timezone_from_fuzzymatch(locale)

        # if the current request is our default timezone, save it.         
        if locale == self.location_timezone:
            self.default_timezone = timezone
        return timezone

    def get_local_datetime(self, location, dtUTC=None):
        if not dtUTC:
            dtUTC = now_utc()
        if self.display_tz:
            # User requested times be shown in some timezone
            tz = self.display_tz
        else:
            tz = self.get_timezone(self.location_timezone)

        if location:
            tz = self.get_timezone(location)
        if not tz:
            self.speak_dialog("time.tz.not.found", {"location": location})
            return None

        return dtUTC.astimezone(tz)
    
    @skill_api_method
    def get_display_date(self, day=None, location=None):
        if not day:
            day = self.get_local_datetime(location)
        if self.config_core.get('date_format') == 'MDY':
            return day.strftime("%-m/%-d/%Y")
        else:
            return day.strftime("%Y/%-d/%-m")

    @skill_api_method
    def get_display_current_time(self, location=None, dtUTC=None):
        # Get a formatted digital clock time based on the user preferences
        dt = self.get_local_datetime(location, dtUTC)
        if not dt:
            return None

        return nice_time(dt, self.lang, speech=False,
                         use_24hour=self.use_24hour)

    def get_spoken_current_time(self, location=None,
                                dtUTC=None, force_ampm=False):
        # Get a formatted spoken time based on the user preferences
        dt = self.get_local_datetime(location, dtUTC)
        if not dt:
            return

        # speak AM/PM when talking about somewhere else
        say_am_pm = bool(location) or force_ampm

        s = nice_time(dt, self.lang, speech=True,
                      use_24hour=self.use_24hour, use_ampm=say_am_pm)
        # HACK: Mimic 2 has a bug with saying "AM".  Work around it for now.
        if say_am_pm:
            s = s.replace("AM", "A.M.")

        return s

    def display(self, display_time):
        if display_time:
            if self.platform == "mycroft_mark_1":
                self.display_mark1(display_time)
            self.display_gui(display_time)

    def display_mark1(self, display_time):
        # Map characters to the display encoding for a Mark 1
        # (4x8 except colon, which is 2x8)
        code_dict = {
            ':': 'CIICAA',
            '0': 'EIMHEEMHAA',
            '1': 'EIIEMHAEAA',
            '2': 'EIEHEFMFAA',
            '3': 'EIEFEFMHAA',
            '4': 'EIMBABMHAA',
            '5': 'EIMFEFEHAA',
            '6': 'EIMHEFEHAA',
            '7': 'EIEAEAMHAA',
            '8': 'EIMHEFMHAA',
            '9': 'EIMBEBMHAA',
        }

        # clear screen (draw two blank sections, numbers cover rest)
        if len(display_time) == 4:
            # for 4-character times, 9x8 blank
            self.enclosure.mouth_display(img_code="JIAAAAAAAAAAAAAAAAAA",
                                         refresh=False)
            self.enclosure.mouth_display(img_code="JIAAAAAAAAAAAAAAAAAA",
                                         x=22, refresh=False)
        else:
            # for 5-character times, 7x8 blank
            self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                         refresh=False)
            self.enclosure.mouth_display(img_code="HIAAAAAAAAAAAAAA",
                                         x=24, refresh=False)

        # draw the time, centered on display
        xoffset = (32 - (4*(len(display_time))-2)) / 2
        for c in display_time:
            if c in code_dict:
                self.enclosure.mouth_display(img_code=code_dict[c],
                                             x=xoffset, refresh=False)
                if c == ":":
                    xoffset += 2  # colon is 1 pixels + a space
                else:
                    xoffset += 4  # digits are 3 pixels + a space

        if self._is_alarm_set():
            # Show a dot in the upper-left
            self.enclosure.mouth_display(img_code="CIAACA", x=29,
                                         refresh=False)
        else:
            self.enclosure.mouth_display(img_code="CIAAAA", x=29,
                                         refresh=False)

    def _is_alarm_set(self):
        """Query the alarm skill if an alarm is set."""
        query = Message("private.mycroftai.has_alarm")
        msg = self.bus.wait_for_response(query)
        return msg and msg.data.get("active_alarms", 0) > 0

    def display_gui(self, display_time):
        """ Display time on the Mycroft GUI. """
        self.gui.clear()
        self.gui['time_string'] = display_time
        self.gui['ampm_string'] = ''
        self.gui['date_string'] = self.get_display_date()
        self.gui.show_page('time.qml')

    def _is_display_idle(self):
        # check if the display is being used by another skill right now
        # or _get_active() == "TimeSkill"
        return self.enclosure.display_manager.get_active() == ''

    def update_display(self, force=False):
        # Don't show idle time when answering a query to prevent
        # overwriting the displayed value.
        if self.answering_query:
            return

        self.gui['time_string'] = self.get_display_current_time()
        self.gui['date_string'] = self.get_display_date()
        self.gui['ampm_string'] = ''  # TODO
        self.gui['weekday_string'] = self.get_weekday()
        self.gui['month_string'] = self.get_month_date()

        if self.settings.get("show_time", False):
            # user requested display of time while idle
            if (force is True) or self._is_display_idle():
                current_time = self.get_display_current_time()
                if self.displayed_time != current_time:
                    self.displayed_time = current_time
                    self.display(current_time)
                    # return mouth to 'idle'
                    self.enclosure.display_manager.remove_active()
            else:
                self.displayed_time = None  # another skill is using display
        else:
            # time display is not wanted
            if self.displayed_time:
                if self._is_display_idle():
                    # erase the existing displayed time
                    self.enclosure.mouth_reset()
                    # return mouth to 'idle'
                    self.enclosure.display_manager.remove_active()
                self.displayed_time = None

    def _extract_location(self, utt):
        # if "Location" in message.data:
        #     return message.data["Location"]
        rx_file = self.find_resource('location.rx', 'regex')
        if rx_file:
            with open(rx_file) as f:
                for pat in f.read().splitlines():
                    pat = pat.strip()
                    if pat and pat[0] == "#":
                        continue
                    res = re.search(pat, utt)
                    if res:
                        try:
                            return res.group("Location")
                        except IndexError:
                            pass
        return None

    ######################################################################
    # Time queries / display

    @intent_handler(IntentBuilder("").require("Query").require("Time").
                    optionally("Location"))
    def handle_query_time(self, message):
        utt = message.data.get('utterance', "")
        location = self._extract_location(utt)
        current_time = self.get_spoken_current_time(location)
        if not current_time:
            return

        # speak it
        self.speak_dialog("time.current", {"time": current_time})

        # and briefly show the time
        self.answering_query = True
        self.enclosure.deactivate_mouth_events()
        self.display(self.get_display_current_time(location))
        time.sleep(5)
        mycroft.audio.wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.activate_mouth_events()
        self.answering_query = False
        self.displayed_time = None

    @intent_handler("what.time.is.it.intent")
    def handle_current_time_simple(self, message):
        self.handle_query_time(message)

    @intent_handler("what.time.will.it.be.intent")
    def handle_query_future_time(self, message):
        utt = normalize(message.data.get('utterance', "").lower())
        extract = extract_datetime(utt)
        dt = None
        if extract:
            dt, utt = extract
        else:
            self.handle_query_time(message)
            return

        location = self._extract_location(utt)
        future_time = self.get_spoken_current_time(location, dt, True)
        if not future_time:
            return

        # speak it
        self.speak_dialog("time.future", {"time": future_time})

        # and briefly show the time
        self.answering_query = True
        self.enclosure.deactivate_mouth_events()
        self.display(self.get_display_current_time(location, dt))
        time.sleep(5)
        mycroft.audio.wait_while_speaking()
        self.enclosure.mouth_reset()
        self.enclosure.activate_mouth_events()
        self.answering_query = False
        self.displayed_time = None

    @intent_handler(IntentBuilder("").optionally("Query").
                    require("Time").require("Future").optionally("Location"))
    def handle_future_time_simple(self, message):
        self.handle_query_future_time(message)

    @intent_handler(IntentBuilder("").require("Display").require("Time").
                    optionally("Location"))
    def handle_show_time(self, message):
        self.display_tz = None
        utt = message.data.get('utterance', "")
        location = self._extract_location(utt)
        if location:
            tz = self.get_timezone(location)
            if not tz:
                self.speak_dialog("time.tz.not.found", {"location": location})
                return
            else:
                self.display_tz = tz
        else:
            self.display_tz = None

        # show time immediately
        self.settings["show_time"] = True
        self.update_display(True)

    ######################################################################
    # Date queries

    def handle_query_date(self, message, response_type="simple"):
        utt = message.data.get('utterance', "").lower()
        try:
            extract = extract_datetime(utt)
        except Exception:
            self.speak_dialog('date.not.found')
            return
        day = extract[0] if extract else now_local()

        # check if a Holiday was requested, e.g. "What day is Christmas?"
        year = extract_number(utt)
        if not year or year < 1500 or year > 3000:  # filter out non-years
            year = day.year

        location = self._extract_location(utt)
        today = to_local(now_utc())
        if location:
            # TODO: Timezone math!
            if (day.year == today.year and day.month == today.month
                    and day.day == today.day):
                day = now_utc()  # for questions ~ "what is the day in sydney"
            day = self.get_local_datetime(location, dtUTC=day)
        if not day:
            return  # failed in timezone lookup

        speak_date = nice_date(day, lang=self.lang)
        # speak it
        if response_type == "simple":
            self.speak_dialog("date", {"date": speak_date})
        elif response_type == "relative":
            # remove time data to get clean dates
            day_date = day.replace(hour=0, minute=0,
                                   second=0, microsecond=0)
            today_date = today.replace(hour=0, minute=0,
                                       second=0, microsecond=0)
            num_days = (day_date - today_date).days
            if num_days >= 0:
                speak_num_days = nice_duration(num_days * 86400)
                self.speak_dialog("date.relative.future",
                                  {"date": speak_date,
                                   "num_days": speak_num_days})
            else:
                # if in the past, make positive before getting duration
                speak_num_days = nice_duration(num_days * -86400)
                self.speak_dialog("date.relative.past",
                                  {"date": speak_date,
                                   "num_days": speak_num_days})

        # and briefly show the date
        self.answering_query = True
        self.show_date(location, day=day)
        time.sleep(10)
        mycroft.audio.wait_while_speaking()
        if self.platform == "mycroft_mark_1":
            self.enclosure.mouth_reset()
            self.enclosure.activate_mouth_events()
        self.answering_query = False
        self.displayed_time = None

    @intent_handler(IntentBuilder("").require("Query").require("Date").
                    optionally("Location"))
    def handle_query_date_simple(self, message):
        self.handle_query_date(message, response_type="simple")

    @intent_handler(IntentBuilder("").require("Query").require("Month"))
    def handle_day_for_date(self, message):
        self.handle_query_date(message, response_type="relative")

    @intent_handler(IntentBuilder("").require("Query").require("RelativeDay")
                                     .optionally("Date"))
    def handle_query_relative_date(self, message):
        if self.voc_match(message.data.get('utterance', ""), 'Today'):
            self.handle_query_date(message, response_type="simple")
        else:
            self.handle_query_date(message, response_type="relative")

    @intent_handler(IntentBuilder("").require("RelativeDay").require("Date"))
    def handle_query_relative_date_alt(self, message):
        if self.voc_match(message.data.get('utterance', ""), 'Today'):
            self.handle_query_date(message, response_type="simple")
        else:
            self.handle_query_date(message, response_type="relative")

    @intent_handler("date.future.weekend.intent")
    def handle_date_future_weekend(self, message):
        # Strip year off nice_date as request is inherently close
        # Don't pass `now` to `nice_date` as a
        # request on Friday will return "tomorrow"
        saturday_date = ', '.join(nice_date(extract_datetime(
                        'this saturday', None, 'en-us')[0]).split(', ')[:2])
        sunday_date = ', '.join(nice_date(extract_datetime(
                      'this sunday', None, 'en-us')[0]).split(', ')[:2])
        self.speak_dialog('date.future.weekend', {
            'saturday_date': saturday_date,
            'sunday_date': sunday_date
        })

    @intent_handler("date.last.weekend.intent")
    def handle_date_last_weekend(self, message):
        # Strip year off nice_date as request is inherently close
        # Don't pass `now` to `nice_date` as a
        # request on Monday will return "yesterday"
        saturday_date = ', '.join(nice_date(extract_datetime(
                        'last saturday', None, 'en-us')[0]).split(', ')[:2])
        sunday_date = ', '.join(nice_date(extract_datetime(
                      'last sunday', None, 'en-us')[0]).split(', ')[:2])
        self.speak_dialog('date.last.weekend', {
            'saturday_date': saturday_date,
            'sunday_date': sunday_date
        })

    @intent_handler(IntentBuilder("").require("Query").require("LeapYear"))
    def handle_query_next_leap_year(self, message):
        now = datetime.datetime.now()
        leap_date = datetime.datetime(now.year, 2, 28)
        year = now.year if now <= leap_date else now.year + 1
        next_leap_year = self.get_next_leap_year(year)
        self.speak_dialog('next.leap.year', {'year': next_leap_year})

    def show_date(self, location, day=None):
        if self.platform == "mycroft_mark_1":
            self.show_date_mark1(location, day)
        self.show_date_gui(location, day)

    def show_date_mark1(self, location, day):
        show = self.get_display_date(day, location)
        self.enclosure.deactivate_mouth_events()
        self.enclosure.mouth_text(show)

    @skill_api_method
    def get_weekday(self, day=None, location=None):
        if not day:
            day = self.get_local_datetime(location)
        if self.lang in date_time_format.lang_config.keys():
            localized_day_names = list(
                 date_time_format.lang_config[self.lang]['weekday'].values())
            weekday = localized_day_names[day.weekday()]
        else:
            weekday = day.strftime("%A")
        return weekday.capitalize()

    @skill_api_method
    def get_month_date(self, day=None, location=None):
        if not day:
            day = self.get_local_datetime(location)
        if self.lang in date_time_format.lang_config.keys():
            localized_month_names = date_time_format.lang_config[self.lang]['month']
            month = localized_month_names[str(int(day.strftime("%m")))]
        else:
            month = day.strftime("%B")
        month = month.capitalize()
        if self.config_core.get('date_format') == 'MDY':
            return "{} {}".format(month, day.strftime("%d"))
        else:
            return "{} {}".format(day.strftime("%d"), month)

    @skill_api_method
    def get_year(self, day=None, location=None):
        if not day:
            day = self.get_local_datetime(location)
        return day.strftime("%Y")

    def get_next_leap_year(self, year):
        next_year = year + 1
        if self.is_leap_year(next_year):
            return next_year
        else:
            return self.get_next_leap_year(next_year)

    def is_leap_year(self, year):
        return (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0))

    def show_date_gui(self, location, day):
        self.gui.clear()
        self.gui['date_string'] = self.get_display_date(day, location)
        self.gui['weekday_string'] = self.get_weekday(day, location)
        self.gui['daymonth_string'] = self.get_month_date(day, location)
        self.gui['location_string'] = str(location)
        month_string = self.get_month_date(day, location).split(" ")
        if self.config_core.get('date_format') == 'MDY':
            self.gui['day_string'] = month_string[1]
            self.gui['month_string'] = month_string[0]
        else:
            self.gui['day_string'] = month_string[0]
            self.gui['month_string'] = month_string[1]
        self.gui['year_string'] = self.get_year(day, location)
        self.gui.show_page('date.qml')


def create_skill():
    return TimeSkill()
