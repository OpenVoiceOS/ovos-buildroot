# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending
import datetime
import time

import lingua_franca
import pytest
import random
import sys
import shutil
import unittest
import datetime as dt

from threading import Event
from os import mkdir, remove
from os.path import dirname, join, exists
from dateutil.tz import gettz
from lingua_franca.format import nice_date_time, nice_duration
from mock import Mock
from mock.mock import call
from mycroft_bus_client import Message
from ovos_utils.events import EventSchedulerInterface
from ovos_utils.messagebus import FakeBus
from lingua_franca import load_language

from mycroft.util.format import nice_time

sys.path.append(dirname(dirname(__file__)))
from util import AlertType, AlertState, AlertPriority, Weekdays
from util.alert import Alert
from util.alert_manager import AlertManager, get_alert_id

examples_dir = join(dirname(__file__), "example_messages")


def _get_message_from_file(filename: str):
    with open(join(examples_dir, filename)) as f:
        contents = f.read()
    return Message.deserialize(contents)


class TestSkill(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from mycroft.skills.skill_loader import SkillLoader

        cls.bus = FakeBus()
        cls.bus.run_in_thread()
        skill_loader = SkillLoader(cls.bus, dirname(dirname(__file__)))
        skill_loader.load()
        cls.skill = skill_loader.instance
        cls.test_fs = join(dirname(__file__), "skill_fs")
        if not exists(cls.test_fs):
            mkdir(cls.test_fs)
        cls.skill.settings_write_path = cls.test_fs
        cls.skill.file_system.path = cls.test_fs

        # Override speak and speak_dialog to test passed arguments
        cls.skill.speak = Mock()
        cls.skill.speak_dialog = Mock()

        # Setup alerts
        load_language("en-us")

        cls.valid_user = "test_user"
        cls.invalid_user = "other_user"
        valid_context = {"username": cls.valid_user}
        invalid_context = {"username": cls.invalid_user}
        sea_tz = gettz("America/Los_Angeles")
        now_time = dt.datetime.now(sea_tz).replace(microsecond=0)
        next_alarm_1_time = now_time + dt.timedelta(days=1)
        next_alarm_2_time = next_alarm_1_time + dt.timedelta(hours=1)
        next_alarm_3_time = next_alarm_2_time + dt.timedelta(minutes=1)
        next_reminder_time = now_time + dt.timedelta(days=2)
        invalid_reminder_time = now_time + dt.timedelta(hours=1)
        invalid_timer_time = now_time + dt.timedelta(minutes=1)

        cls.valid_alarm_1 = Alert.create(next_alarm_1_time, "Alarm 1",
                                         AlertType.ALARM,
                                         context=valid_context)
        cls.valid_alarm_2 = Alert.create(next_alarm_2_time, "Alarm 2",
                                         AlertType.ALARM,
                                         context=valid_context)
        cls.valid_alarm_3 = Alert.create(next_alarm_3_time, "Alarm 3",
                                         AlertType.ALARM,
                                         context=valid_context)
        cls.valid_reminder = Alert.create(next_reminder_time, "Valid Reminder",
                                          AlertType.REMINDER,
                                          context=valid_context)
        cls.other_reminder = Alert.create(invalid_reminder_time,
                                          "Other Reminder",
                                          AlertType.REMINDER,
                                          context=invalid_context)
        cls.other_timer = Alert.create(invalid_timer_time, "Other Timer",
                                       AlertType.TIMER, context=invalid_context)
        for a in {cls.other_timer, cls.other_reminder, cls.valid_reminder,
                  cls.valid_alarm_3, cls.valid_alarm_1, cls.valid_alarm_2}:
            cls.skill.alert_manager.add_alert(a)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.test_fs)

    def tearDown(self) -> None:
        self.skill.speak.reset_mock()
        self.skill.speak_dialog.reset_mock()

    def test_00_skill_init(self):
        # Test any parameters expected to be set in init or initialize methods
        from neon_utils.skills import NeonSkill
        self.assertIsInstance(self.skill, NeonSkill)
        # TODO: This patches import resolution; revert after proper packaging
        # self.assertIsInstance(self.skill.alert_manager, AlertManager)
        self.assertTrue(hasattr(self.skill.alert_manager, "pending_alerts"))

    def test_handle_create_alarm(self):
        real_confirm = self.skill.confirm_alert
        confirm_alert = Mock()
        self.skill.confirm_alert = confirm_alert
        valid_message = _get_message_from_file("create_alarm_daily.json")
        invalid_message = _get_message_from_file("invalid_messages/create_alarm_no_time.json")

        self.skill.handle_create_alarm(invalid_message)
        self.skill.speak_dialog.assert_called_once()
        self.skill.speak_dialog.assert_called_with("error_no_time",
                                                   {"kind": "alarm"},
                                                   private=True)
        self.skill.confirm_alert.assert_not_called()

        self.skill.handle_create_alarm(valid_message)
        self.skill.confirm_alert.assert_called_once()
        self.assertEqual(self.skill.confirm_alert.call_args[0][0].alert_type,
                         AlertType.ALARM)
        self.assertEqual(self.skill.confirm_alert.call_args[0][1],
                         valid_message)

        self.skill.confirm_alert = real_confirm

    def test_handle_create_timer(self):
        real_confirm = self.skill.confirm_alert
        confirm_alert = Mock()
        self.skill.confirm_alert = confirm_alert
        valid_message = _get_message_from_file("set_time_timer.json")
        invalid_message = _get_message_from_file(
            "invalid_messages/create_timer_no_duration.json")

        self.skill.handle_create_timer(invalid_message)
        self.skill.speak_dialog.assert_called_once()
        self.skill.speak_dialog.assert_called_with("error_no_duration",
                                                   private=True)
        self.skill.confirm_alert.assert_not_called()

        self.skill.handle_create_timer(valid_message)
        self.skill.confirm_alert.assert_called_once()
        self.assertEqual(self.skill.confirm_alert.call_args[0][0].alert_type,
                         AlertType.TIMER)
        self.assertEqual(self.skill.confirm_alert.call_args[0][1],
                         valid_message)
        self.assertAlmostEqual(
            self.skill.confirm_alert.call_args[0][2].timestamp(),
            dt.datetime.now().timestamp(), delta=2)

        self.skill.confirm_alert = real_confirm

    def test_handle_create_reminder(self):
        real_confirm = self.skill.confirm_alert
        confirm_alert = Mock()
        self.skill.confirm_alert = confirm_alert
        valid_message = _get_message_from_file(
            "reminder_at_time_to_action.json")
        invalid_message = _get_message_from_file(
            "invalid_messages/remind_me_no_time.json")

        self.skill.handle_create_reminder(invalid_message)
        self.skill.speak_dialog.assert_called_once()
        self.skill.speak_dialog.assert_called_with("error_no_time",
                                                   {"kind": "reminder"},
                                                   private=True)
        self.skill.confirm_alert.assert_not_called()

        self.skill.handle_create_reminder(valid_message)
        self.skill.confirm_alert.assert_called_once()
        self.assertEqual(self.skill.confirm_alert.call_args[0][0].alert_type,
                         AlertType.REMINDER)
        self.assertEqual(self.skill.confirm_alert.call_args[0][1],
                         valid_message)

        self.skill.confirm_alert = real_confirm

    def test_handle_create_reminder_alt(self):
        real_method = self.skill.handle_create_reminder
        create_reminder = Mock()
        self.skill.handle_create_reminder = create_reminder
        test_message = Message("test", {"data": True}, {"context": "test"})
        self.skill.handle_create_reminder_alt(test_message)
        create_reminder.assert_called_once()
        create_reminder.assert_called_with(test_message)

        self.skill.handle_create_reminder = real_method

    def test_handle_create_event(self):
        real_method = self.skill.handle_create_reminder
        create_reminder = Mock()
        self.skill.handle_create_reminder = create_reminder
        test_message = Message("test", {"data": True}, {"context": "test"})
        self.skill.handle_create_event(test_message)
        create_reminder.assert_called_once()
        create_reminder.assert_called_with(test_message)

        self.skill.handle_create_reminder = real_method

    def test_handle_next_alert(self):
        valid_message_alarm = Message("test", {"alarm": "alarm"},
                                      {"username": self.valid_user})
        valid_message_timer = Message("test", {"timer": "timer"},
                                      {"username": self.valid_user})
        valid_message_reminder = Message("test", {"reminder": "reminder"},
                                         {"username": self.valid_user})
        valid_message_all = Message("test", {"alert": "alert"},
                                    {"username": self.valid_user})

        self.skill.handle_next_alert(valid_message_alarm)
        self.skill.speak_dialog.assert_called_with(
            "next_alert_unnamed",
            {"kind": "alarm",
             "name": self.valid_alarm_1.alert_name,
             "time": nice_time(self.valid_alarm_1.next_expiration,
                               use_ampm=True)},
            private=True)

        self.skill.handle_next_alert(valid_message_timer)
        self.skill.speak_dialog.assert_called_with(
            "list_alert_none_upcoming",
            {"kind": "timer"},
            private=True)

        self.skill.handle_next_alert(valid_message_reminder)
        self.skill.speak_dialog.assert_called_with(
            "next_alert_named",
            {"kind": "reminder",
             "name": self.valid_reminder.alert_name,
             "time": nice_time(self.valid_reminder.next_expiration,
                               use_ampm=True)},
            private=True)

        self.skill.handle_next_alert(valid_message_all)
        self.skill.speak_dialog.assert_called_with(
            "next_alert_unnamed",
            {"kind": "alert",
             "name": self.valid_alarm_1.alert_name,
             "time": nice_time(self.valid_alarm_1.next_expiration,
                               use_ampm=True)},
            private=True)

    def test_handle_list_alerts(self):
        valid_message_alarm = Message("test", {"alarm": "alarm"},
                                      {"username": self.valid_user})
        valid_message_timer = Message("test", {"timer": "timer"},
                                      {"username": self.valid_user})
        valid_message_reminder = Message("test", {"reminder": "reminder"},
                                         {"username": self.valid_user})
        valid_message_all = Message("test", {"alert": "alert"},
                                    {"username": self.valid_user})

        self.skill.handle_list_alerts(valid_message_alarm)
        self.skill.speak.assert_called()
        alarms_string = self.skill.speak.call_args[0][0]
        self.assertEqual(len(alarms_string.split('\n')), 4)
        for alarm in {self.valid_alarm_1, self.valid_alarm_2,
                      self.valid_alarm_3}:
            self.assertIn(f"\n{alarm.alert_name} - ", alarms_string)

        self.skill.handle_list_alerts(valid_message_timer)
        self.skill.speak_dialog.assert_called_with("list_alert_none_upcoming",
                                                   {"kind": "timer"},
                                                   private=True)

        self.skill.handle_list_alerts(valid_message_reminder)
        reminder_string = self.skill.speak.call_args[0][0]
        self.assertEqual(len(reminder_string.split('\n')), 2)
        self.assertIn(f"\n{self.valid_reminder.alert_name} - ",
                      reminder_string)

        self.skill.handle_list_alerts(valid_message_all)
        all_string = self.skill.speak.call_args[0][0]
        self.assertEqual(len(all_string.split('\n')), 5)
        for alert in {self.valid_alarm_1, self.valid_alarm_2,
                      self.valid_alarm_3, self.valid_reminder}:
            self.assertIn(f"\n{alert.alert_name} - ", all_string)

    def test_handle_timer_status(self):

        real_timer_status = self.skill._display_timer_gui
        self.skill._display_timer_gui = Mock()

        timer_test_user = "timer_user"
        valid_message = Message("test", {"timer_time_remaining": ""},
                                {"username": timer_test_user})
        sea_tz = gettz("America/Los_Angeles")
        now_time = dt.datetime.now(sea_tz).replace(microsecond=0)
        test_timer = Alert.create(now_time + dt.timedelta(minutes=5),
                                  "5 Minute Timer", AlertType.TIMER,
                                  context={"username": timer_test_user})
        long_timer = Alert.create(now_time + dt.timedelta(minutes=30),
                                  "Oven Timer", AlertType.TIMER,
                                  context={"username": timer_test_user})

        # No active timers
        self.skill.handle_timer_status(valid_message)
        self.skill.speak_dialog.assert_called_once()
        self.skill.speak_dialog.assert_called_with("timer_status_none_active",
                                                   private=True)

        # Single active timer not specifically requested
        self.skill.alert_manager.add_alert(long_timer)
        self.skill.handle_timer_status(valid_message)
        call_args = self.skill.speak_dialog.call_args
        self.assertEqual(call_args[0][0], "timer_status")
        self.assertEqual(call_args[0][1]["timer"], long_timer.alert_name)
        self.assertIsNotNone(call_args[0][1]["duration"])
        self.assertTrue(call_args[1]["private"])
        self.skill._display_timer_gui.assert_called_with(long_timer)

        # Multiple active timers not specifically requested
        self.skill.alert_manager.add_alert(test_timer)
        self.skill.handle_timer_status(valid_message)
        self.skill.speak.assert_called_once()
        spoken_string = self.skill.speak.call_args[0][0]
        self.assertEqual(len(spoken_string.split('\n')), 2)
        self.assertTrue(spoken_string.split('\n')[0].startswith(
            "The 5 Minute Timer has"))
        self.assertTrue(spoken_string.split('\n')[1].startswith(
            "The Oven Timer has"))

        # Multiple active timers, one specifically requested
        valid_message.data["utterance"] = \
            f"how much time is left on {long_timer.alert_name}"
        self.skill.handle_timer_status(valid_message)
        call_args = self.skill.speak_dialog.call_args
        self.assertEqual(call_args[0][0], "timer_status")
        self.assertEqual(call_args[0][1]["timer"], long_timer.alert_name)
        self.assertIsNotNone(call_args[0][1]["duration"])
        self.assertTrue(call_args[1]["private"])
        self.skill._display_timer_gui.assert_called_with(long_timer)

        self.skill.alert_manager.rm_alert(get_alert_id(long_timer))
        self.skill.alert_manager.rm_alert(get_alert_id(test_timer))
        self.skill._display_timer_gui = real_timer_status

    def test_handle_start_quiet_hours(self):
        real_method = self.skill.update_skill_settings
        self.skill.update_skill_settings = Mock()

        message = Message("test", {"quiet_hours_start": "start"},
                          {"username": "tester",
                           "neon_should_respond": True})
        self.skill.handle_start_quiet_hours(message)
        self.skill.speak_dialog.assert_called_once()
        self.skill.speak_dialog.assert_called_with("quiet_hours_start",
                                                   private=True)

        self.skill.update_skill_settings.assert_called_once()
        self.skill.update_skill_settings.assert_called_with(
            {"quiet_hours": True}, message)

        self.skill.update_skill_settings = real_method

    def test_handle_end_quiet_hours(self):
        quiet_hours = True

        def preference_skill(_):
            return {"quiet_hours": quiet_hours}

        real_pref_skill = self.skill.preference_skill
        self.skill.preference_skill = preference_skill
        real_update_settings = self.skill.update_skill_settings
        self.skill.update_skill_settings = Mock()

        test_message = Message("test", {"quiet_hours_end": ""},
                               {"username": self.valid_user,
                                "neon_should_respond": True})

        # Test end active quiet hours, nothing missed
        self.skill.handle_end_quiet_hours(test_message)
        first_call = self.skill.speak_dialog.call_args_list[0]
        second_call = self.skill.speak_dialog.call_args_list[1]
        self.assertEqual(first_call,
                         call("quiet_hours_end", private=True))
        self.assertEqual(second_call,
                         call("list_alert_none_missed", private=True))
        self.skill.update_skill_settings.assert_called_with(
            {"quiet_hours": False}, test_message)

        # Test end active quiet hours, already inactive
        self.skill.speak_dialog.reset_mock()
        self.skill.update_skill_settings.reset_mock()
        quiet_hours = False
        self.skill.handle_end_quiet_hours(test_message)
        self.skill.update_skill_settings.assert_not_called()
        self.skill.speak_dialog.assert_called_once()
        self.skill.speak_dialog.assert_called_with("list_alert_none_missed",
                                                   private=True)

        # TODO: Test with missed alerts DM

        self.skill.preference_skill = real_pref_skill
        self.skill.update_skill_settings = real_update_settings

    def test_handle_cancel_alert(self):
        cancel_test_user = "test_user_cancellation"
        valid_context = {"username": cancel_test_user}
        sea_tz = gettz("America/Los_Angeles")
        now_time = dt.datetime.now(sea_tz).replace(microsecond=0)
        alarm_1_time = now_time + dt.timedelta(days=1)
        alarm_2_time = alarm_1_time + dt.timedelta(hours=1)
        alarm_3_time = now_time.replace(hour=9, minute=30, second=0) + \
                       dt.timedelta(days=1)
        reminder_time = now_time + dt.timedelta(days=2)
        timer_1_time = now_time + dt.timedelta(minutes=5)
        timer_2_time = now_time + dt.timedelta(minutes=10)

        # Define alerts
        tomorrow_alarm = Alert.create(alarm_1_time, alert_type=AlertType.ALARM,
                                      context=valid_context)
        later_alarm = Alert.create(alarm_2_time, alert_type=AlertType.ALARM,
                                   context=valid_context)
        morning_alarm = Alert.create(alarm_3_time, alert_type=AlertType.ALARM,
                                     context=valid_context)
        trash_reminder = Alert.create(reminder_time, "take out garbage",
                                      AlertType.REMINDER,
                                      context=valid_context)
        pasta_timer = Alert.create(timer_1_time, "pasta", AlertType.TIMER,
                                   context=valid_context)
        unnamed_timer = Alert.create(timer_1_time, alert_type=AlertType.TIMER,
                                     context=valid_context)
        oven_timer = Alert.create(timer_2_time, "cherry pie", AlertType.TIMER,
                                  context=valid_context)
        for a in (tomorrow_alarm, later_alarm, morning_alarm, trash_reminder,
                  pasta_timer, oven_timer, unnamed_timer):
            self.skill.alert_manager.add_alert(a)
            self.assertIn(get_alert_id(a),
                          self.skill.alert_manager.pending_alerts.keys())

        # Cancel only alert of type
        message = Message("test", {"cancel": "cancel",
                                   "reminder": "reminder"}, valid_context)
        self.skill.handle_cancel_alert(message)
        self.assertNotIn(get_alert_id(trash_reminder),
                         self.skill.alert_manager.pending_alerts.keys())
        self.skill.speak_dialog.assert_called_with(
            "confirm_cancel_alert", {"kind": "reminder",
                                     "name": trash_reminder.alert_name},
            private=True)
        # Cancel no alerts of requested type
        self.skill.handle_cancel_alert(message)
        self.skill.speak_dialog.assert_called_with(
            "error_no_scheduled_kind_to_cancel", {"kind": "reminder"},
            private=True)

        # Cancel no match
        message = Message("test",
                          {"cancel": "cancel",
                           "timer": "timer",
                           "utterance": "cancel my test timer",
                           "__tags__": [{
                               "match": "cancel",
                               "key": "cancel",
                               "start_token": 0,
                               "end_token": 0},
                               {
                                   "match": "timer",
                                   "key": "timer",
                                   "start_token": 3,
                                   "end_token": 3
                               }
                           ]}, valid_context)
        pending = self.skill.alert_manager.pending_alerts.keys()
        self.skill.handle_cancel_alert(message)
        self.skill.speak_dialog.assert_called_with("error_nothing_to_cancel",
                                                   private=True)
        self.assertEqual(pending,
                         self.skill.alert_manager.pending_alerts.keys())

        # Cancel match name  pasta timer
        message = Message("test",
                          {"cancel": "cancel",
                           "timer": "timer",
                           "utterance": "cancel my pasta timer",
                           "__tags__": [{
                               "match": "cancel",
                               "key": "cancel",
                               "start_token": 0,
                               "end_token": 0},
                               {
                                   "match": "timer",
                                   "key": "timer",
                                   "start_token": 3,
                                   "end_token": 3
                               }
                           ]}, valid_context)
        self.assertIn(get_alert_id(pasta_timer),
                      self.skill.alert_manager.pending_alerts.keys())
        self.skill.handle_cancel_alert(message)
        self.assertNotIn(get_alert_id(pasta_timer),
                         self.skill.alert_manager.pending_alerts.keys())
        self.skill.speak_dialog.assert_called_with(
            "confirm_cancel_alert", {"kind": "timer",
                                     "name": pasta_timer.alert_name},
            private=True)

        # Cancel match time  9:30 AM alarm
        message = Message("test",
                          {"cancel": "cancel",
                           "alarm": "alarm",
                           "utterance": "cancel my 9:30 AM alarm",
                           "__tags__": [{
                               "match": "cancel",
                               "key": "cancel",
                               "start_token": 0,
                               "end_token": 0},
                               {
                                   "match": "alarm",
                                   "key": "alarm",
                                   "start_token": 4,
                                   "end_token": 4
                               }
                           ]}, valid_context)
        self.assertIn(get_alert_id(morning_alarm),
                      self.skill.alert_manager.pending_alerts.keys())
        self.skill.handle_cancel_alert(message)
        self.assertNotIn(get_alert_id(morning_alarm),
                         self.skill.alert_manager.pending_alerts.keys())
        self.skill.speak_dialog.assert_called_with(
            "confirm_cancel_alert", {"kind": "alarm",
                                     "name": morning_alarm.alert_name},
            private=True)

        # Cancel partial name oven (cherry pie)
        message = Message("test",
                          {"cancel": "cancel",
                           "timer": "timer",
                           "utterance": "cancel my pie timer",
                           "__tags__": [{
                               "match": "cancel",
                               "key": "cancel",
                               "start_token": 0,
                               "end_token": 0},
                               {
                                   "match": "timer",
                                   "key": "timer",
                                   "start_token": 3,
                                   "end_token": 3
                               }
                           ]}, valid_context)
        self.assertIn(get_alert_id(oven_timer),
                      self.skill.alert_manager.pending_alerts.keys())
        self.skill.handle_cancel_alert(message)
        self.assertNotIn(get_alert_id(oven_timer),
                         self.skill.alert_manager.pending_alerts.keys())
        self.skill.speak_dialog.assert_called_with(
            "confirm_cancel_alert", {"kind": "timer",
                                     "name": oven_timer.alert_name},
            private=True)

        # Cancel all valid
        message = Message("test", {"cancel": "cancel",
                                   "alert": "alert",
                                   "all": "all"}, valid_context)
        self.skill.handle_cancel_alert(message)
        self.skill.speak_dialog.assert_called_with("confirm_cancel_all",
                                                   {"kind": "alert"},
                                                   private=True)
        self.assertEqual(
            self.skill.alert_manager.get_user_alerts(cancel_test_user),
            {"missed": list(), "active": list(), "pending": list()}
        )

        # Cancel all nothing to cancel
        self.skill.handle_cancel_alert(message)
        self.skill.speak_dialog.assert_called_with("error_nothing_to_cancel",
                                                   private=True)

    def test_confirm_alert(self):
        # TODO
        pass

    def test_alert_expired(self):
        # TODO
        pass

    def test_run_notify_expired(self):
        # TODO
        pass

    def test_play_notify_expired(self):
        # TODO
        pass

    def test_speak_notify_expired(self):
        # TODO
        pass

    def test_gui_timer_status(self):
        # TODO
        pass

    def test_gui_notify_expired(self):
        # TODO
        pass

    def test_resolve_requested_alert(self):
        # TODO
        pass

    def test_get_events(self):
        # TODO
        pass

    def test_get_requested_alert_name_and_time(self):
        # TODO
        pass

    def test_get_alert_type_from_intent(self):
        # TODO
        pass

    def test_get_user_tz(self):
        # TODO
        pass

    def test_get_alert_dialog_data(self):
        real_translate = self.skill.translate
        self.skill.translate = Mock()
        self.skill.translate.return_value = "repeat"

        now_time = datetime.datetime.now(datetime.timezone.utc)
        # Alert for tomorrow at 9 AM
        tomorrow_alert_time = (now_time +
                               datetime.timedelta(days=2)).replace(
            hour=9, minute=0, second=0, microsecond=0)
        # Alert for later today
        today_alert_time = now_time + datetime.timedelta(minutes=1)
        # TODO: Above will fail if run at 11:59PM; consider better mocking
        # Alarm later today
        today_alert = Alert.create(today_alert_time, "Today Alarm",
                                   AlertType.ALARM)
        dialog = self.skill._get_alert_dialog_data(today_alert, 'en', False)
        self.skill.translate.assert_not_called()
        self.assertEqual(dialog,
                         {'name': 'Today Alarm',
                          'time': nice_time(today_alert.next_expiration
                                            , use_24hour=False,
                                            use_ampm=True)})

        # One time alarm not today
        one_time = Alert.create(tomorrow_alert_time, "One Time Alarm",
                                AlertType.ALARM)
        dialog = self.skill._get_alert_dialog_data(one_time, 'en', False)
        self.skill.translate.assert_not_called()
        self.assertEqual(dialog,
                         {'name': 'One Time Alarm',
                          'time': nice_date_time(one_time.next_expiration,
                                                 use_24hour=False,
                                                 use_ampm=True)})

        # Weekend alarm
        weekend = Alert.create(tomorrow_alert_time, "Weekend Alarm",
                               AlertType.ALARM,
                               repeat_days={Weekdays.SUN, Weekdays.SAT})
        dialog = self.skill._get_alert_dialog_data(weekend, 'en', False)
        self.skill.translate.assert_called_with('word_weekend')
        self.assertEqual(dialog,
                         {'name': 'Weekend Alarm',
                          'repeat': 'repeat',
                          'time': nice_date_time(one_time.next_expiration,
                                                 use_24hour=False,
                                                 use_ampm=True)})

        # Weekday reminder
        weekday = Alert.create(tomorrow_alert_time, "Weekday Reminder",
                               AlertType.REMINDER,
                               repeat_days={Weekdays.MON, Weekdays.TUE,
                                            Weekdays.WED, Weekdays.THU,
                                            Weekdays.FRI})
        dialog = self.skill._get_alert_dialog_data(weekday, 'en', False)
        self.skill.translate.assert_called_with('word_weekday')
        self.assertEqual(dialog,
                         {'name': 'Weekday Reminder',
                          'repeat': 'repeat',
                          'time': nice_date_time(one_time.next_expiration,
                                                 use_24hour=False,
                                                 use_ampm=True)})

        # Daily reminder
        daily = Alert.create(tomorrow_alert_time, "Daily Reminder",
                             AlertType.REMINDER,
                             repeat_days={Weekdays.MON, Weekdays.TUE,
                                          Weekdays.WED, Weekdays.THU,
                                          Weekdays.FRI, Weekdays.SAT,
                                          Weekdays.SUN})
        dialog = self.skill._get_alert_dialog_data(daily, 'en', False)
        self.skill.translate.assert_called_with('word_day')
        self.assertEqual(dialog,
                         {'name': 'Daily Reminder',
                          'repeat': 'repeat',
                          'time': nice_date_time(one_time.next_expiration,
                                                 use_24hour=False,
                                                 use_ampm=True)})

        # Weekly Reminder
        weekly = Alert.create(tomorrow_alert_time, "Weekly Reminder",
                              AlertType.REMINDER,
                              repeat_days={Weekdays.MON})
        dialog = self.skill._get_alert_dialog_data(weekly, 'en', False)
        self.skill.translate.assert_called_with('word_weekday_monday')
        self.assertEqual(dialog,
                         {'name': 'Weekly Reminder',
                          'repeat': 'repeat',
                          'time': nice_date_time(one_time.next_expiration,
                                                 use_24hour=False,
                                                 use_ampm=True)})

        # 8 hour reminder
        eight_hour = Alert.create(tomorrow_alert_time, "Eight Hour Reminder",
                                  AlertType.REMINDER,
                                  repeat_frequency=datetime.timedelta(hours=8))
        dialog = self.skill._get_alert_dialog_data(eight_hour, 'en', False)
        self.assertEqual(dialog,
                         {'name': 'Eight Hour Reminder',
                          'repeat': nice_duration(
                              datetime.timedelta(hours=8).total_seconds()),
                          'time': nice_date_time(one_time.next_expiration,
                                                 use_24hour=False,
                                                 use_ampm=True)})
        self.skill.translate = real_translate

    def test_get_spoken_alert_type(self):
        # TODO
        pass

    def test_get_spoken_weekday(self):
        # TODO
        pass


class TestAlert(unittest.TestCase):
    def test_alert_create(self):
        now_time_valid = dt.datetime.now(dt.timezone.utc)
        now_time_invalid = dt.datetime.now()
        end_repeat_valid = now_time_valid + dt.timedelta(days=14)
        end_repeat_invalid = now_time_invalid + dt.timedelta(days=14)

        with self.assertRaises(ValueError):
            Alert.create(now_time_invalid)

        with self.assertRaises(ValueError):
            Alert.create(now_time_valid, end_repeat=end_repeat_invalid)

        test_alert = Alert.create(
            now_time_valid + dt.timedelta(hours=1),
            "test alert name",
            AlertType.ALARM,
            AlertPriority.HIGHEST.value,
            3600, None,
            end_repeat_valid,
            "audio_file", "script_file",
            {"testing": True}
        )

        # Test alert dump/reload
        dumped_alert = test_alert.data
        self.assertIsInstance(dumped_alert, dict)
        self.assertEqual(dumped_alert, Alert.from_dict(dumped_alert).data)

        # Test alert serialize/deserialize
        serial_alert = test_alert.serialize
        self.assertIsInstance(serial_alert, str)
        self.assertEqual(serial_alert,
                         Alert.deserialize(serial_alert).serialize)

    def test_alert_properties(self):
        now_time_valid = \
            dt.datetime.now(dt.timezone.utc)
        end_repeat_valid = now_time_valid + dt.timedelta(days=14)

        future_alert_no_repeat = Alert.create(
            now_time_valid + dt.timedelta(hours=1),
            "test alert name",
            AlertType.ALARM,
            AlertPriority.HIGHEST.value,
            3600, None,
            end_repeat_valid,
            "audio_file", "script_file",
            {"testing": True}
        )

        # Test alert properties
        self.assertEqual(future_alert_no_repeat.alert_type, AlertType.ALARM)
        self.assertEqual(future_alert_no_repeat.priority, 10)
        self.assertEqual(future_alert_no_repeat.end_repeat,
                         end_repeat_valid.replace(microsecond=0))
        self.assertIsNone(future_alert_no_repeat.repeat_days)
        self.assertEqual(future_alert_no_repeat.repeat_frequency,
                         dt.timedelta(seconds=3600))
        self.assertEqual(future_alert_no_repeat.context, {"testing": True})
        self.assertEqual(future_alert_no_repeat.alert_name, "test alert name")
        self.assertEqual(future_alert_no_repeat.audio_file, "audio_file")
        self.assertEqual(future_alert_no_repeat.script_filename, "script_file")
        self.assertFalse(future_alert_no_repeat.is_expired)
        self.assertEqual(future_alert_no_repeat.next_expiration,
                         now_time_valid.replace(microsecond=0) +
                         dt.timedelta(hours=1))
        self.assertIsInstance(future_alert_no_repeat.time_to_expiration,
                              dt.timedelta)

        expired_alert_no_repeat = Alert.create(
            now_time_valid - dt.timedelta(hours=1),
            "expired alert name",
            AlertType.REMINDER,
            AlertPriority.AVERAGE.value,
            None, None, None,
            "audio_file", "script_file",
            {"testing": True}
        )
        # Test alert properties
        self.assertEqual(expired_alert_no_repeat.alert_type,
                         AlertType.REMINDER)
        self.assertEqual(expired_alert_no_repeat.priority, 5)
        self.assertIsNone(expired_alert_no_repeat.end_repeat)
        self.assertIsNone(expired_alert_no_repeat.repeat_days)
        self.assertIsNone(expired_alert_no_repeat.repeat_frequency)
        self.assertEqual(expired_alert_no_repeat.context, {"testing": True})
        self.assertEqual(expired_alert_no_repeat.alert_name,
                         "expired alert name")
        self.assertEqual(expired_alert_no_repeat.audio_file, "audio_file")
        self.assertEqual(expired_alert_no_repeat.script_filename,
                         "script_file")
        self.assertTrue(expired_alert_no_repeat.is_expired)
        self.assertIsNone(expired_alert_no_repeat.next_expiration)
        self.assertLessEqual(expired_alert_no_repeat.time_to_expiration.total_seconds(), 0)

        expired_alert_expired_repeat = Alert.create(
            now_time_valid - dt.timedelta(hours=6),
            "expired alert name",
            repeat_frequency=dt.timedelta(hours=1),
            end_repeat=now_time_valid - dt.timedelta(hours=1),
            context={"testing": True}
        )
        # Test alert properties
        self.assertEqual(expired_alert_expired_repeat.repeat_frequency,
                         dt.timedelta(hours=1))
        self.assertIsInstance(expired_alert_expired_repeat.end_repeat,
                              dt.datetime)
        self.assertIsNone(expired_alert_expired_repeat.repeat_days)
        self.assertEqual(expired_alert_expired_repeat.context,
                         {"testing": True})
        self.assertEqual(expired_alert_expired_repeat.alert_name,
                         "expired alert name")
        self.assertTrue(expired_alert_expired_repeat.is_expired)
        self.assertIsNone(expired_alert_expired_repeat.next_expiration)
        self.assertLessEqual(expired_alert_expired_repeat.time_to_expiration.total_seconds(), 0)

        alert_time = now_time_valid.replace(microsecond=0) - \
                     dt.timedelta(hours=1)
        expired_alert_weekday_repeat = Alert.create(
            alert_time,
            "expired weekly alert name",
            repeat_days={Weekdays(alert_time.weekday())},
            context={"testing": True}
        )
        # Test alert properties
        self.assertIsNone(expired_alert_weekday_repeat.end_repeat)
        self.assertEqual(expired_alert_weekday_repeat.repeat_days,
                         {Weekdays(alert_time.weekday())})
        self.assertIsNone(expired_alert_weekday_repeat.repeat_frequency)
        self.assertEqual(expired_alert_weekday_repeat.context,
                         {"testing": True})
        self.assertEqual(expired_alert_weekday_repeat.alert_name,
                         "expired weekly alert name")
        self.assertTrue(expired_alert_weekday_repeat.is_expired)
        self.assertIsInstance(expired_alert_weekday_repeat.next_expiration,
                              dt.datetime)
        self.assertFalse(expired_alert_weekday_repeat.is_expired)
        self.assertEqual(expired_alert_weekday_repeat.next_expiration,
                         alert_time + dt.timedelta(weeks=1))

        # Comparison is rounded to account for processing time
        self.assertAlmostEqual(expired_alert_weekday_repeat.
                               time_to_expiration.total_seconds(),
                               dt.timedelta(weeks=1, hours=-1).total_seconds(),
                               delta=5)

    def test_alert_add_context(self):
        alert_time = dt.datetime.now(dt.timezone.utc)
        original_context = {"testing": True}
        alert = Alert.create(
            alert_time,
            "test alert context",
            context=original_context
        )
        self.assertEqual(alert.context, original_context)
        alert.add_context({"ident": "ident"})
        self.assertEqual(alert.context, {"ident": "ident",
                                         "testing": True})
        alert.add_context({"ident": "new_ident"})
        self.assertEqual(alert.context, {"ident": "new_ident",
                                         "testing": True})


class TestAlertManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manager_path = join(dirname(__file__), "test_cache")

    def _init_alert_manager(self):
        alert_expired = Mock()

        # Load empty cache
        test_file = join(self.manager_path, "alerts.json")
        scheduler = EventSchedulerInterface("test")
        alert_manager = AlertManager(test_file, scheduler, alert_expired)
        return alert_manager

    def test_alert_manager_init(self):
        called = Event()
        test_alert: Alert = None

        def alert_expired(alert: Alert):
            nonlocal test_alert
            self.assertEqual(alert.data, test_alert.data)
            called.set()

        now_time = dt.datetime.now(dt.timezone.utc)
        past_alert = Alert.create(now_time + dt.timedelta(minutes=-1))
        future_alert = Alert.create(now_time + dt.timedelta(minutes=5))
        repeat_alert = Alert.create(now_time,
                                    repeat_frequency=dt.timedelta(seconds=1))

        # Load empty cache
        test_file = join(self.manager_path, "alerts.json")
        scheduler = EventSchedulerInterface("test")
        alert_manager = AlertManager(test_file, scheduler, alert_expired)
        self.assertEqual(alert_manager.missed_alerts, dict())
        self.assertEqual(alert_manager.pending_alerts, dict())
        self.assertEqual(alert_manager.active_alerts, dict())

        # Add past alert
        with self.assertRaises(ValueError):
            alert_manager.add_alert(past_alert)

        # Add valid alert
        alert_id = alert_manager.add_alert(future_alert)
        self.assertIn(alert_id, alert_manager.pending_alerts)
        self.assertEqual(len(scheduler.events.events), 1)
        self.assertEqual(alert_manager.pending_alerts[alert_id]
                         .next_expiration, future_alert.next_expiration)
        self.assertEqual(alert_manager.get_alert_status(alert_id),
                         AlertState.PENDING)

        # Remove valid alert
        alert_manager.rm_alert(alert_id)
        self.assertNotIn(alert_id, alert_manager.pending_alerts)
        self.assertEqual(len(scheduler.events.events), 0)
        self.assertIsNone(alert_manager.get_alert_status(alert_id))

        def _make_active_alert(ident, alert):
            nonlocal test_alert
            test_alert = alert
            self.assertIn(ident, alert_manager.pending_alerts)
            data = alert.data
            context = alert.context
            message = Message(f"alert.{ident}", data, context)
            self.assertEqual(alert_manager.get_alert_status(ident),
                             AlertState.PENDING)
            alert_manager._handle_alert_expiration(message)
            self.assertTrue(called.wait(5))
            self.assertIn(ident, alert_manager.active_alerts)
            self.assertEqual(alert_manager.active_alerts[ident].data,
                             alert.data)
            self.assertEqual(alert_manager.get_alert_status(ident),
                             AlertState.ACTIVE)

        # Handle dismiss active alert no repeat
        alert_id = alert_manager.add_alert(future_alert)
        _make_active_alert(alert_id, future_alert)
        dismissed_alert = alert_manager.dismiss_active_alert(alert_id)
        self.assertEqual(dismissed_alert.data, future_alert.data)

        # Mark active alert as missed (no repeat)
        alert_id = alert_manager.add_alert(future_alert)
        _make_active_alert(alert_id, future_alert)
        alert_manager.mark_alert_missed(alert_id)
        self.assertEqual(alert_manager.active_alerts, dict())
        self.assertIn(alert_id, alert_manager.missed_alerts)
        self.assertEqual(alert_manager.missed_alerts[alert_id].data,
                         future_alert.data)
        self.assertEqual(alert_manager.get_alert_status(alert_id),
                         AlertState.MISSED)

        # Dismiss missed alert
        missed_alert = alert_manager.dismiss_missed_alert(alert_id)
        self.assertEqual(missed_alert.data, future_alert.data)
        self.assertEqual(alert_manager.missed_alerts, dict())

        # Schedule repeating alert
        alert_id = alert_manager.add_alert(repeat_alert)
        _make_active_alert(alert_id, repeat_alert)
        self.assertIn(alert_id, alert_manager.pending_alerts)
        self.assertIn(alert_id, alert_manager.active_alerts)
        alert_manager.mark_alert_missed(alert_id)
        self.assertIn(alert_id, alert_manager.missed_alerts)
        self.assertIn(alert_id, alert_manager.pending_alerts)
        self.assertNotIn(alert_id, alert_manager.active_alerts)

        # Dismiss repeating alert
        missed_alert = alert_manager.dismiss_missed_alert(alert_id)
        self.assertEqual(missed_alert.data, repeat_alert.data)
        self.assertIn(alert_id, alert_manager.pending_alerts)
        self.assertNotIn(alert_id, alert_manager.missed_alerts)
        self.assertNotIn(alert_id, alert_manager.active_alerts)

    def test_alert_manager_caching(self):
        alert_expired = Mock()

        # Load empty cache
        test_file = join(self.manager_path, "alerts.json")
        scheduler = EventSchedulerInterface("test")
        alert_manager = AlertManager(test_file, scheduler, alert_expired)

        now_time = dt.datetime.now(dt.timezone.utc)
        future_alert = Alert.create(now_time + dt.timedelta(minutes=5))
        repeat_alert = Alert.create(now_time,
                                    repeat_frequency=dt.timedelta(seconds=1))

        # Add alerts to manager
        alert_manager.add_alert(future_alert)
        alert_id = alert_manager.add_alert(repeat_alert)
        # Cancel the event that would usually be cancelled on expiration
        scheduler.cancel_scheduled_event(alert_id)
        alert_manager._handle_alert_expiration(repeat_alert)
        self.assertEqual(len(alert_manager.pending_alerts), 2)
        self.assertEqual(len(alert_manager.active_alerts), 1)
        self.assertEqual(alert_manager.missed_alerts, dict())

        # Check scheduled events
        self.assertEqual(len(scheduler.events.events), 2)

        # Shutdown manager
        alert_manager.shutdown()
        self.assertFalse(scheduler.events.events)

        # Create new manager
        new_manager = AlertManager(test_file, scheduler, alert_expired)
        self.assertEqual(len(new_manager.pending_alerts), 2)
        self.assertEqual(len(new_manager.missed_alerts), 1)
        self.assertEqual(new_manager.active_alerts, dict())
        self.assertEqual(alert_manager.pending_alerts.keys(),
                         new_manager.pending_alerts.keys())

        # Check scheduled events
        self.assertEqual(len(scheduler.events.events), 2)

        remove(test_file)

    def test_get_user_alerts(self):
        from util.alert_manager import get_alert_user
        alert_manager = self._init_alert_manager()
        now_time = dt.datetime.now(dt.timezone.utc)
        for i in range(10):
            if i in range(5):
                user = "test_user"
            else:
                user = "other_user"
            alert_time = now_time + dt.timedelta(minutes=random.randint(1, 60))
            alert = Alert.create(alert_time, context={"user": user})
            alert_manager.add_alert(alert)

        test_user_alerts = alert_manager.get_user_alerts("test_user")
        other_user_alerts = alert_manager.get_user_alerts("other_user")
        self.assertEqual(len(test_user_alerts["pending"]), 5)
        self.assertEqual(len(other_user_alerts["pending"]), 5)
        self.assertTrue(all([get_alert_user(alert) == "test_user" for alert in
                             [*test_user_alerts["pending"],
                              *test_user_alerts["active"],
                              *test_user_alerts["missed"]]]))
        self.assertTrue(all([get_alert_user(alert) == "other_user" for alert in
                             [*other_user_alerts["pending"],
                              *other_user_alerts["active"],
                              *other_user_alerts["missed"]]]))

    def test_get_all_alerts(self):
        alert_manager = self._init_alert_manager()
        now_time = dt.datetime.now(dt.timezone.utc)
        for i in range(15):
            if i in range(10):
                user = "test_user"
            else:
                user = "other_user"
            alert_time = now_time + dt.timedelta(minutes=random.randint(1, 60))
            alert = Alert.create(alert_time, context={"user": user})
            alert_manager.add_alert(alert)

        all_alerts = alert_manager.get_all_alerts()
        self.assertEqual(len(all_alerts["pending"]), 15)
        for i in range(1, len(all_alerts)):
            self.assertLessEqual(all_alerts["pending"][i - 1].next_expiration,
                                 all_alerts["pending"][i].next_expiration)

    def test_get_alert_user(self):
        from util.alert_manager import get_alert_user, _DEFAULT_USER
        test_user = "tester"
        alert_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)
        alert_no_user = Alert.create(alert_time)
        alert_with_user = Alert.create(alert_time, context={"user": test_user})
        self.assertEqual(get_alert_user(alert_no_user), _DEFAULT_USER)
        self.assertEqual(get_alert_user(alert_with_user), test_user)

        alert_no_user.add_context({"user": test_user})
        self.assertEqual(get_alert_user(alert_no_user), test_user)
        alert_no_user.add_context({"user": "new_user"})
        self.assertEqual(get_alert_user(alert_no_user), "new_user")

    def test_get_alert_id(self):
        from util.alert_manager import get_alert_id
        alert_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)
        alert_no_id = Alert.create(alert_time)
        alert_with_id = Alert.create(alert_time, context={"ident": "test"})

        self.assertIsNone(get_alert_id(alert_no_id))
        self.assertEqual(get_alert_id(alert_with_id), "test")

    def test_sort_alerts_list(self):
        from copy import deepcopy
        from util.alert_manager import sort_alerts_list
        now_time = dt.datetime.now(dt.timezone.utc)
        alerts = list()

        for i in range(10):
            alert_time = now_time + dt.timedelta(minutes=random.randint(1, 60))
            alert = Alert.create(alert_time)
            alerts.append(alert)

        unsorted = deepcopy(alerts)
        alerts = sort_alerts_list(alerts)
        self.assertEqual(len(unsorted), len(alerts))
        self.assertEqual(len(alerts), 10)
        for i in range(1, len(alerts)):
            self.assertLessEqual(alerts[i - 1].next_expiration,
                                 alerts[i].next_expiration)

    def test_get_alert_by_type(self):
        from util.alert_manager import get_alerts_by_type
        now_time = dt.datetime.now(dt.timezone.utc)
        alerts = list()

        for i in range(15):
            if i in range(5):
                alert_type = AlertType.ALARM
            elif i in range(10):
                alert_type = AlertType.TIMER
            else:
                alert_type = AlertType.REMINDER
            alert_time = now_time + dt.timedelta(minutes=random.randint(1, 60))
            alert = Alert.create(alert_time, alert_type=alert_type)
            alerts.append(alert)

        by_type = get_alerts_by_type(alerts)
        alarms = by_type[AlertType.ALARM]
        timers = by_type[AlertType.TIMER]
        reminders = by_type[AlertType.REMINDER]
        for alert in alarms:
            self.assertIsInstance(alert, Alert)
            self.assertEqual(alert.alert_type, AlertType.ALARM)
        for alert in timers:
            self.assertIsInstance(alert, Alert)
            self.assertEqual(alert.alert_type, AlertType.TIMER)
        for alert in reminders:
            self.assertIsInstance(alert, Alert)
            self.assertEqual(alert.alert_type, AlertType.REMINDER)

    # TODO: Test Snooze Alert


class TestParseUtils(unittest.TestCase):
    def test_round_nearest_minute(self):
        from util.parse_utils import round_nearest_minute
        now_time = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        alert_time = now_time + dt.timedelta(minutes=9, seconds=5)
        rounded = round_nearest_minute(alert_time)
        self.assertEqual(rounded, alert_time)

        rounded = round_nearest_minute(alert_time, dt.timedelta(minutes=5))
        self.assertEqual(rounded, alert_time.replace(second=0))

    def test_spoken_time_remaining(self):
        from util.parse_utils import spoken_time_remaining
        now_time = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        seconds_alert = now_time + dt.timedelta(minutes=59, seconds=59)
        to_speak = spoken_time_remaining(seconds_alert, now_time)
        self.assertTrue(all([word for word in ("minutes", "seconds")
                             if word in to_speak.split()]))
        self.assertEqual(to_speak, "fifty nine minutes fifty nine seconds")

        minutes_alert = now_time + dt.timedelta(hours=23, minutes=59,
                                                seconds=59)
        to_speak = spoken_time_remaining(minutes_alert, now_time)
        self.assertTrue(all([word for word in ("hours", "minutes")
                             if word in to_speak.split()]))
        self.assertNotIn("seconds", to_speak.split())
        self.assertEqual(to_speak, "twenty three hours fifty nine minutes")

        hours_alert = now_time + dt.timedelta(days=6, hours=23, minutes=59,
                                              seconds=59)
        to_speak = spoken_time_remaining(hours_alert, now_time)
        self.assertTrue(all([word for word in ("days", "hours")
                             if word in to_speak.split()]))
        self.assertTrue(all([not word for word in ("minutes", "seconds")
                             if word in to_speak.split()]))
        self.assertEqual(to_speak, "six days twenty three hours")

        days_alert = now_time + dt.timedelta(weeks=1, days=1, hours=1,
                                             minutes=1, seconds=1)
        to_speak = spoken_time_remaining(days_alert, now_time)
        self.assertTrue(all([word for word in ("days",)
                             if word in to_speak.split()]))
        self.assertTrue(all([not word for word in ("hours", "minutes",
                                                   "seconds")
                             if word in to_speak.split()]))
        self.assertEqual(to_speak, "eight days")

    def test_get_default_alert_name(self):
        from util.parse_utils import get_default_alert_name
        now_time = dt.datetime.now(dt.timezone.utc)
        timer_time = now_time + dt.timedelta(minutes=10)
        self.assertEqual(get_default_alert_name(timer_time,
                                                AlertType.TIMER, now_time),
                         "ten minutes timer")
        timer_time = now_time + dt.timedelta(hours=6, seconds=1)
        self.assertEqual(get_default_alert_name(timer_time,
                                                AlertType.TIMER, now_time),
                         "six hours timer")

        alarm_time = (now_time + dt.timedelta(days=1)).replace(hour=8,
                                                               minute=0,
                                                               second=0)
        self.assertEqual(get_default_alert_name(alarm_time, AlertType.ALARM),
                         "8:00 AM alarm")
        self.assertEqual(get_default_alert_name(alarm_time, AlertType.ALARM,
                                                use_24hour=True),
                         "08:00 alarm")

        reminder_time = alarm_time + dt.timedelta(hours=12)
        self.assertEqual(get_default_alert_name(reminder_time,
                                                AlertType.REMINDER),
                         "8:00 PM reminder")
        self.assertEqual(get_default_alert_name(reminder_time,
                                                AlertType.REMINDER,
                                                use_24hour=True),
                         "20:00 reminder")

    def test_tokenize_utterance_alarm(self):
        from util.parse_utils import tokenize_utterance

        daily = _get_message_from_file("create_alarm_daily.json")
        tokens = tokenize_utterance(daily)
        self.assertEqual(tokens, ['create', 'an', 'alarm', 'for 10', 'daily'])

        weekly = _get_message_from_file("create_alarm_every_tuesday.json")
        tokens = tokenize_utterance(weekly)
        self.assertEqual(tokens, ['set', 'an', 'alarm', 'for 9 am', 'every',
                                  'tuesday'])

        weekdays = _get_message_from_file("create_alarm_weekdays.json")
        tokens = tokenize_utterance(weekdays)
        self.assertEqual(tokens, ['set', 'an', 'alarm', 'for 8 am on',
                                  'weekdays'])

        weekends = _get_message_from_file("wake_me_up_weekends.json")
        tokens = tokenize_utterance(weekends)
        self.assertEqual(tokens, ['wake me up', 'at 9 30 AM on',
                                  'weekends'])

        wakeup_at = _get_message_from_file("wake_me_up_at_time_alarm.json")
        tokens = tokenize_utterance(wakeup_at)
        self.assertEqual(tokens, ['neon', 'wake me up', 'at 7 am'])

        wakeup_in = _get_message_from_file("wake_me_up_in_time_alarm.json")
        tokens = tokenize_utterance(wakeup_in)
        self.assertEqual(tokens, ['wake me up', 'in 8 hours'])

        multi_day_repeat = \
            _get_message_from_file("alarm_every_monday_thursday.json")
        tokens = tokenize_utterance(multi_day_repeat)
        self.assertEqual(tokens, ['wake me up', 'every',
                                  'monday and thursday at 9 am'])

    def test_get_unmatched_tokens_alarm(self):
        from util.parse_utils import get_unmatched_tokens

        daily = _get_message_from_file("create_alarm_daily.json")
        tokens = get_unmatched_tokens(daily)
        self.assertIsInstance(tokens, list)
        self.assertEqual(tokens, ['an', 'for 10'])

        weekly = _get_message_from_file("create_alarm_every_tuesday.json")
        tokens = get_unmatched_tokens(weekly)
        self.assertIsInstance(tokens, list)
        self.assertEqual(tokens, ['an', 'for 9 am', 'tuesday'])

        weekdays = _get_message_from_file("create_alarm_weekdays.json")
        tokens = get_unmatched_tokens(weekdays)
        self.assertIsInstance(tokens, list)
        self.assertEqual(tokens, ['an', 'for 8 am on'])

        weekends = _get_message_from_file("wake_me_up_weekends.json")
        tokens = get_unmatched_tokens(weekends)
        self.assertEqual(tokens, ['at 9 30 AM on'])

        wakeup_at = _get_message_from_file("wake_me_up_at_time_alarm.json")
        tokens = get_unmatched_tokens(wakeup_at)
        self.assertIsInstance(tokens, list)
        self.assertEqual(tokens, ['neon', 'at 7 am'])

        wakeup_in = _get_message_from_file("wake_me_up_in_time_alarm.json")
        tokens = get_unmatched_tokens(wakeup_in)
        self.assertIsInstance(tokens, list)
        self.assertEqual(tokens, ['in 8 hours'])

        multi_day_repeat = \
            _get_message_from_file("alarm_every_monday_thursday.json")
        tokens = get_unmatched_tokens(multi_day_repeat)
        self.assertEqual(tokens, ['monday and thursday at 9 am'])

    def test_parse_repeat_from_message(self):
        from util.parse_utils import parse_repeat_from_message, \
            tokenize_utterance

        daily = _get_message_from_file("create_alarm_daily.json")
        repeat = parse_repeat_from_message(daily)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [Weekdays.MON, Weekdays.TUE, Weekdays.WED,
                                  Weekdays.THU, Weekdays.FRI, Weekdays.SAT,
                                  Weekdays.SUN])

        weekly = _get_message_from_file("create_alarm_every_tuesday.json")
        tokens = tokenize_utterance(weekly)
        repeat = parse_repeat_from_message(weekly, tokens)
        self.assertNotIn("tuesday", tokens)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [Weekdays.TUE])

        weekdays = _get_message_from_file("create_alarm_weekdays.json")
        repeat = parse_repeat_from_message(weekdays)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [Weekdays.MON, Weekdays.TUE, Weekdays.WED,
                                  Weekdays.THU, Weekdays.FRI])

        weekends = _get_message_from_file("wake_me_up_weekends.json")
        repeat = parse_repeat_from_message(weekends)
        self.assertEqual(repeat, [Weekdays.SAT, Weekdays.SUN])

        wakeup_at = _get_message_from_file("wake_me_up_at_time_alarm.json")
        repeat = parse_repeat_from_message(wakeup_at)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [])

        wakeup_in = _get_message_from_file("wake_me_up_in_time_alarm.json")
        repeat = parse_repeat_from_message(wakeup_in)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [])

        multi_day_repeat = \
            _get_message_from_file("alarm_every_monday_thursday.json")
        tokens = tokenize_utterance(multi_day_repeat)
        repeat = parse_repeat_from_message(multi_day_repeat, tokens)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [Weekdays.MON, Weekdays.THU])
        self.assertEqual(tokens, ["wake me up", "every", "and", "at 9 am"])

        daily_reminder = _get_message_from_file(
            "remind_me_for_duration_to_action_every_repeat.json")
        repeat = parse_repeat_from_message(daily_reminder)
        self.assertIsInstance(repeat, list)
        self.assertEqual(repeat, [Weekdays.MON, Weekdays.TUE, Weekdays.WED,
                                  Weekdays.THU, Weekdays.FRI, Weekdays.SAT,
                                  Weekdays.SUN])

        every_12_hours_reminder = _get_message_from_file(
            "reminder_every_interval_to_action_for_duration.json")
        tokens = tokenize_utterance(every_12_hours_reminder)
        repeat = parse_repeat_from_message(every_12_hours_reminder, tokens)
        self.assertEqual(repeat, dt.timedelta(hours=12))
        self.assertEqual(tokens, ["remind me", "every",
                                  "to take my antibiotics",
                                  "for the next", "week"])

        every_8_hours_reminder = _get_message_from_file(
            "set_reminder_to_action_every_interval_until_end.json"
        )
        tokens = tokenize_utterance(every_8_hours_reminder)
        repeat = parse_repeat_from_message(every_8_hours_reminder, tokens)
        self.assertEqual(repeat, dt.timedelta(hours=8))
        self.assertEqual(tokens, ["set", "a", "reminder",
                                  "to rotate logs", "every",
                                  "until", "next sunday"])

    def test_parse_end_condition_from_message(self):
        from util.parse_utils import parse_end_condition_from_message
        now_time = dt.datetime.now(dt.timezone.utc)

        for_the_next_four_weeks = _get_message_from_file(
            "remind_me_for_duration_to_action_every_repeat.json")
        for_the_next_week = _get_message_from_file(
            "reminder_every_interval_to_action_for_duration.json"
        )
        until_next_sunday = _get_message_from_file(
            "set_reminder_to_action_every_interval_until_end.json"
        )

        next_month = parse_end_condition_from_message(for_the_next_four_weeks)
        self.assertEqual(next_month.date(),
                         (now_time + dt.timedelta(weeks=4)).date())

        next_week = parse_end_condition_from_message(for_the_next_week)
        self.assertEqual(next_week.date(),
                         (now_time + dt.timedelta(days=7)).date())

        next_sunday = parse_end_condition_from_message(until_next_sunday)
        self.assertEqual(next_sunday.weekday(), Weekdays.SUN)
        self.assertGreaterEqual(next_sunday, now_time)

    def test_parse_alert_time_from_message_alarm(self):
        from util.parse_utils import parse_alert_time_from_message, \
            tokenize_utterance

        daily = _get_message_from_file("create_alarm_daily.json")
        alert_time = parse_alert_time_from_message(daily)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertIn(alert_time.time(), (dt.time(hour=10), dt.time(hour=22)))

        weekly = _get_message_from_file("create_alarm_every_tuesday.json")
        tokens = tokenize_utterance(weekly)
        alert_time = parse_alert_time_from_message(weekly, tokens)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertEqual(alert_time.time(), dt.time(hour=9))
        self.assertNotIn("for 9 am", tokens)

        weekdays = _get_message_from_file("create_alarm_weekdays.json")
        alert_time = parse_alert_time_from_message(weekdays)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertEqual(alert_time.time(), dt.time(hour=8))

        weekends = _get_message_from_file("wake_me_up_weekends.json")
        alert_time = parse_alert_time_from_message(weekends)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertEqual(alert_time.time(), dt.time(hour=9, minute=30))

        wakeup_at = _get_message_from_file("wake_me_up_at_time_alarm.json")
        alert_time = parse_alert_time_from_message(wakeup_at)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertEqual(alert_time.time(), dt.time(hour=7))

        tz = gettz("America/Los_Angeles")
        wakeup_in = _get_message_from_file("wake_me_up_in_time_alarm.json")
        alert_time = parse_alert_time_from_message(wakeup_in, timezone=tz)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertEqual(alert_time.tzinfo, tz)

        valid_alert_time = \
            dt.datetime.now(tz) + dt.timedelta(hours=8)

        self.assertEqual(valid_alert_time.tzinfo, tz)
        self.assertAlmostEqual(alert_time.timestamp(),
                               valid_alert_time.timestamp(), 0)

        multi_day_repeat = \
            _get_message_from_file("alarm_every_monday_thursday.json")
        alert_time = parse_alert_time_from_message(multi_day_repeat)
        self.assertIsInstance(alert_time, dt.datetime)
        self.assertEqual(alert_time.tzinfo, dt.timezone.utc)
        self.assertEqual(alert_time.time(), dt.time(hour=9))

    def test_parse_alert_time_from_message_timer(self):
        from util.parse_utils import parse_alert_time_from_message
        sea_tz = gettz("America/Los_Angeles")
        no_name_10_minutes = _get_message_from_file("set_time_timer.json")
        baking_12_minutes = _get_message_from_file("start_named_timer.json")
        bread_20_minutes = _get_message_from_file("start_timer_for_name.json")
        no_name_utc = parse_alert_time_from_message(no_name_10_minutes)
        no_name_local = parse_alert_time_from_message(no_name_10_minutes,
                                                      timezone=sea_tz)
        baking_utc = parse_alert_time_from_message(baking_12_minutes)
        baking_local = parse_alert_time_from_message(baking_12_minutes,
                                                     timezone=sea_tz)
        bread_utc = parse_alert_time_from_message(bread_20_minutes)
        bread_local = parse_alert_time_from_message(bread_20_minutes,
                                                    timezone=sea_tz)
        self.assertAlmostEqual(no_name_utc.timestamp(),
                               no_name_local.timestamp(), 0)
        self.assertAlmostEqual(baking_utc.timestamp(),
                               baking_local.timestamp(), 0)
        self.assertAlmostEqual(bread_utc.timestamp(),
                               bread_local.timestamp(), 0)

    def test_parse_alert_time_from_message_reminder(self):
        # TODO
        pass

    def test_parse_alert_priority_from_message(self):
        # TODO
        pass

    def test_parse_audio_file_from_message(self):
        # TODO
        pass

    def test_parse_script_file_from_message(self):
        # TODO
        pass

    def test_parse_alert_name_from_message(self):
        from util.parse_utils import parse_alert_name_from_message
        monday_thursday_alarm = _get_message_from_file(
            "alarm_every_monday_thursday.json")
        daily_alarm = _get_message_from_file("create_alarm_daily.json")
        tuesday_alarm = _get_message_from_file(
            "create_alarm_every_tuesday.json")
        weekday_alarm = _get_message_from_file("create_alarm_weekdays.json")
        wakeup_at_time_alarm = _get_message_from_file(
            "wake_me_up_at_time_alarm.json")
        wakeup_in_time_alarm = _get_message_from_file(
            "wake_me_up_in_time_alarm.json")
        wakeup_weekends = _get_message_from_file("wake_me_up_weekends.json")

        set_unnamed_timer = _get_message_from_file("set_time_timer.json")
        start_unnamed_timer = _get_message_from_file(
            "start_timer_for_time.json")
        baking_timer = _get_message_from_file("start_named_timer.json")
        bread_timer = _get_message_from_file("start_timer_for_name.json")

        exercise_reminder = _get_message_from_file(
            "remind_me_for_duration_to_action_every_repeat.json")
        dinner_reminder = _get_message_from_file(
            "reminder_at_time_to_action.json")
        antibiotics_reminder = _get_message_from_file(
            "reminder_every_interval_to_action_for_duration.json")
        break_reminder = _get_message_from_file(
            "reminder_in_duration_to_action.json")
        meeting_reminder = _get_message_from_file(
            "reminder_to_action_at_time.json")
        alt_dinner_reminder = _get_message_from_file(
            "reminder_to_action_in_duration.json")
        medication_reminder = _get_message_from_file(
            "set_action_reminder_for_time.json")
        rotate_logs_reminder = _get_message_from_file(
            "set_reminder_to_action_every_interval_until_end.json")

        with open(join(dirname(dirname(__file__)),
                       "locale", "en-us", "articles.voc")) as f:
            articles = f.read().split('\n')

        self.assertIsNone(parse_alert_name_from_message(monday_thursday_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(daily_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(tuesday_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(weekday_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(wakeup_at_time_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(wakeup_in_time_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(wakeup_weekends,
                                                        strip_datetimes=True,
                                                        articles=articles))

        self.assertIsNone(parse_alert_name_from_message(set_unnamed_timer,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(start_unnamed_timer,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(monday_thursday_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))
        self.assertIsNone(parse_alert_name_from_message(monday_thursday_alarm,
                                                        strip_datetimes=True,
                                                        articles=articles))

        self.assertEqual(parse_alert_name_from_message(baking_timer,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "baking")
        self.assertEqual(parse_alert_name_from_message(bread_timer,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "bread")

        self.assertEqual(parse_alert_name_from_message(exercise_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "exercise")
        self.assertEqual(parse_alert_name_from_message(dinner_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "start making dinner")
        self.assertEqual(parse_alert_name_from_message(antibiotics_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "take antibiotics")
        self.assertEqual(parse_alert_name_from_message(break_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "take break")
        self.assertEqual(parse_alert_name_from_message(meeting_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "start meeting")
        self.assertEqual(parse_alert_name_from_message(alt_dinner_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "start dinner")
        self.assertEqual(parse_alert_name_from_message(medication_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "medication")
        self.assertEqual(parse_alert_name_from_message(rotate_logs_reminder,
                                                       strip_datetimes=True,
                                                       articles=articles),
                         "rotate logs")

    def test_parse_alert_context_from_message(self):
        from util.parse_utils import parse_alert_context_from_message, \
            _DEFAULT_USER
        test_message_no_context = Message("test", {}, {})
        test_message_local_user = Message("test", {},
                                          {"user": "local",
                                           "timing": {
                                               "handle_utterance":
                                                   1644629287.028714,
                                               "transcribed":
                                                   1644629287.028714,
                                               "save_transcript":
                                                   8.821487426757812e-06,
                                               "text_parsers":
                                                   4.553794860839844e-05
                                           },
                                           "ident": "1644629287"
                                           })
        test_message_klat_data = Message("test", {}, {"user": "server_user",
                                                      "klat_data": {
                                                          "cid": "test_cid",
                                                          "sid": "test_sid",
                                                          "domain": "Private",
                                                          "flac_filename": "ff"
                                                      },
                                                      })

        no_context = parse_alert_context_from_message(test_message_no_context)
        self.assertEqual(no_context["user"], _DEFAULT_USER)
        self.assertIsInstance(no_context["ident"], str)
        self.assertIsInstance(no_context["created"], float)

        local_user = parse_alert_context_from_message(test_message_local_user)
        self.assertEqual(local_user["user"], "local")
        self.assertEqual(local_user["ident"], "1644629287")
        self.assertEqual(local_user["created"], 1644629287.028714)
        self.assertIsInstance(local_user["timing"], dict)

        klat_user = parse_alert_context_from_message(test_message_klat_data)
        self.assertEqual(klat_user["user"], "server_user")
        self.assertIsInstance(klat_user["ident"], str)
        self.assertIsInstance(klat_user["created"], float)
        self.assertIsInstance(klat_user["klat_data"], dict)

    def test_build_alert_from_intent_alarm(self):
        from util.parse_utils import build_alert_from_intent
        seattle_tz = gettz("America/Los_Angeles")
        utc_tz = dt.timezone.utc

        daily = _get_message_from_file("create_alarm_daily.json")
        wakeup_at = _get_message_from_file("wake_me_up_at_time_alarm.json")
        wakeup_in = _get_message_from_file("wake_me_up_in_time_alarm.json")

        daily_alert_seattle = build_alert_from_intent(daily, AlertType.ALARM,
                                                      seattle_tz)
        daily_alert_utc = build_alert_from_intent(daily, AlertType.ALARM,
                                                  utc_tz)

        def _validate_daily(alert: Alert):
            self.assertEqual(alert.alert_type, AlertType.ALARM)
            self.assertIsInstance(alert.priority, int)
            self.assertIsNone(alert.end_repeat)
            self.assertEqual(len(alert.repeat_days), 7)
            self.assertIsNone(alert.repeat_frequency)
            self.assertIsInstance(alert.context, dict)
            self.assertIsInstance(alert.alert_name, str)
            self.assertIsNone(alert.audio_file)
            self.assertIsNone(alert.script_filename)
            self.assertFalse(alert.is_expired)
            self.assertGreaterEqual(alert.time_to_expiration,
                                    dt.timedelta(seconds=1))
            self.assertIn(alert.next_expiration.time(),
                          (dt.time(hour=10), dt.time(hour=22)))

        _validate_daily(daily_alert_seattle)
        _validate_daily(daily_alert_utc)
        self.assertNotEqual(
            daily_alert_seattle.time_to_expiration.total_seconds(),
            daily_alert_utc.time_to_expiration.total_seconds())

        wakeup_at_alert_seattle = build_alert_from_intent(wakeup_at,
                                                          AlertType.ALARM,
                                                          seattle_tz)
        wakeup_at_alert_utc = build_alert_from_intent(wakeup_at,
                                                      AlertType.ALARM,
                                                      utc_tz)

        def _validate_wakeup_at(alert: Alert):
            self.assertEqual(alert.alert_type, AlertType.ALARM)
            self.assertIsInstance(alert.priority, int)
            self.assertIsNone(alert.end_repeat)
            self.assertIsNone(alert.repeat_days)
            self.assertIsNone(alert.repeat_frequency)
            self.assertIsInstance(alert.context, dict)
            self.assertIsInstance(alert.alert_name, str)
            self.assertIsNone(alert.audio_file)
            self.assertIsNone(alert.script_filename)
            self.assertFalse(alert.is_expired)
            self.assertGreaterEqual(alert.time_to_expiration,
                                    dt.timedelta(seconds=1))
            self.assertEqual(alert.next_expiration.time(), dt.time(hour=7))

        _validate_wakeup_at(wakeup_at_alert_seattle)
        _validate_wakeup_at(wakeup_at_alert_utc)
        self.assertEqual(wakeup_at_alert_seattle.alert_name,
                         wakeup_at_alert_utc.alert_name)
        self.assertEqual(wakeup_at_alert_utc.alert_name,
                         "7:00 AM alarm")
        self.assertNotEqual(wakeup_at_alert_seattle.time_to_expiration,
                            wakeup_at_alert_utc.time_to_expiration)

        wakeup_in_alert_seattle = build_alert_from_intent(wakeup_in,
                                                          AlertType.ALARM,
                                                          seattle_tz)
        wakeup_in_alert_utc = build_alert_from_intent(wakeup_in,
                                                      AlertType.ALARM,
                                                      utc_tz)

        def _validate_wakeup_in(alert: Alert):
            self.assertEqual(alert.alert_type, AlertType.ALARM)
            self.assertIsInstance(alert.priority, int)
            self.assertIsNone(alert.end_repeat)
            self.assertIsNone(alert.repeat_days)
            self.assertIsNone(alert.repeat_frequency)
            self.assertIsInstance(alert.context, dict)
            self.assertIsInstance(alert.alert_name, str)
            self.assertIsNone(alert.audio_file)
            self.assertIsNone(alert.script_filename)
            self.assertFalse(alert.is_expired)
            self.assertAlmostEqual(alert.time_to_expiration.total_seconds(),
                                   dt.timedelta(hours=8).total_seconds(),
                                   delta=2)

        _validate_wakeup_in(wakeup_in_alert_seattle)
        _validate_wakeup_in(wakeup_in_alert_utc)
        self.assertAlmostEqual(wakeup_in_alert_seattle.time_to_expiration
                               .total_seconds(),
                               wakeup_in_alert_utc.time_to_expiration
                               .total_seconds(), delta=2)

    def test_build_alert_from_intent_timer(self):
        from util.parse_utils import build_alert_from_intent
        sea_tz = gettz("America/Los_Angeles")
        no_name_10_minutes = _get_message_from_file("set_time_timer.json")
        baking_12_minutes = _get_message_from_file("start_named_timer.json")
        bread_20_minutes = _get_message_from_file("start_timer_for_name.json")

        def _validate_alert_default_params(timer: Alert):
            self.assertEqual(timer.alert_type, AlertType.TIMER)
            self.assertIsInstance(timer.priority, int)
            self.assertIsNone(timer.end_repeat)
            self.assertIsNone(timer.repeat_days)
            self.assertIsNone(timer.repeat_frequency)
            self.assertIsInstance(timer.context, dict)
            self.assertIsInstance(timer.alert_name, str)
            self.assertIsNone(timer.audio_file)
            self.assertIsNone(timer.script_filename)
            self.assertFalse(timer.is_expired)
            self.assertIsInstance(timer.time_to_expiration, dt.timedelta)
            self.assertIsInstance(timer.next_expiration, dt.datetime)

        no_name_timer_utc = build_alert_from_intent(no_name_10_minutes,
                                                    AlertType.TIMER,
                                                    dt.timezone.utc)
        no_name_timer_sea = build_alert_from_intent(no_name_10_minutes,
                                                    AlertType.TIMER,
                                                    sea_tz)
        _validate_alert_default_params(no_name_timer_utc)
        _validate_alert_default_params(no_name_timer_sea)
        self.assertAlmostEqual(
            no_name_timer_sea.time_to_expiration.total_seconds(),
            no_name_timer_utc.time_to_expiration.total_seconds(), 0)

        baking_timer_sea = build_alert_from_intent(baking_12_minutes,
                                                   AlertType.TIMER,
                                                   sea_tz)
        _validate_alert_default_params(baking_timer_sea)
        self.assertEqual(baking_timer_sea.alert_name, "baking")

        bread_timer_sea = build_alert_from_intent(bread_20_minutes,
                                                  AlertType.TIMER,
                                                  sea_tz)
        _validate_alert_default_params(bread_timer_sea)
        self.assertEqual(bread_timer_sea.alert_name, "bread")

    def test_build_alert_from_intent_reminder(self):
        from util.parse_utils import build_alert_from_intent
        sea_tz = gettz("America/Los_Angeles")
        now_local = dt.datetime.now(sea_tz).replace(microsecond=0)

        def _validate_alert_default_params(reminder: Alert):
            self.assertEqual(reminder.alert_type, AlertType.REMINDER)
            self.assertIsInstance(reminder.priority, int)
            self.assertIsInstance(reminder.context, dict)
            self.assertIsInstance(reminder.alert_name, str)
            self.assertIsNone(reminder.audio_file)
            self.assertIsNone(reminder.script_filename)
            self.assertFalse(reminder.is_expired)
            self.assertIsInstance(reminder.time_to_expiration, dt.timedelta)
            self.assertIsInstance(reminder.next_expiration, dt.datetime)

        exercise_reminder = _get_message_from_file(
            "remind_me_for_duration_to_action_every_repeat.json")
        dinner_reminder = _get_message_from_file(
            "reminder_at_time_to_action.json")
        antibiotics_reminder = _get_message_from_file(
            "reminder_every_interval_to_action_for_duration.json")
        break_reminder = _get_message_from_file(
            "reminder_in_duration_to_action.json")
        meeting_reminder = _get_message_from_file(
            "reminder_to_action_at_time.json")
        alt_dinner_reminder = _get_message_from_file(
            "reminder_to_action_in_duration.json")
        medication_reminder = _get_message_from_file(
            "set_action_reminder_for_time.json")
        rotate_logs_reminder = _get_message_from_file(
            "set_reminder_to_action_every_interval_until_end.json")

        exercise_reminder = build_alert_from_intent(exercise_reminder,
                                                    AlertType.REMINDER, sea_tz)
        _validate_alert_default_params(exercise_reminder)
        self.assertEqual(exercise_reminder.next_expiration.time(),
                         dt.time(hour=10))
        self.assertEqual(exercise_reminder.alert_name, "exercise")
        self.assertEqual(len(exercise_reminder.repeat_days), 7)
        self.assertIsNone(exercise_reminder.repeat_frequency)
        self.assertEqual(exercise_reminder.end_repeat.date(),
                         (now_local + dt.timedelta(weeks=4)).date())

        dinner_reminder = build_alert_from_intent(dinner_reminder,
                                                  AlertType.REMINDER, sea_tz)
        _validate_alert_default_params(dinner_reminder)
        self.assertEqual(dinner_reminder.next_expiration.time(),
                         dt.time(hour=19))
        self.assertEqual(dinner_reminder.alert_name, "start making dinner")
        self.assertIsNone(dinner_reminder.repeat_days)
        self.assertIsNone(dinner_reminder.repeat_frequency)
        self.assertIsNone(dinner_reminder.end_repeat)

        antibiotics_reminder = build_alert_from_intent(antibiotics_reminder,
                                                       AlertType.REMINDER,
                                                       sea_tz)
        self.assertEqual(antibiotics_reminder.next_expiration,
                         now_local + dt.timedelta(hours=12))
        self.assertEqual(antibiotics_reminder.alert_name, "take antibiotics")
        self.assertIsNone(antibiotics_reminder.repeat_days)
        self.assertEqual(antibiotics_reminder.repeat_frequency,
                         dt.timedelta(hours=12))
        self.assertEqual(antibiotics_reminder.end_repeat.date(),
                         (now_local + dt.timedelta(weeks=1)).date())

        break_reminder = build_alert_from_intent(break_reminder,
                                                 AlertType.REMINDER, sea_tz)
        self.assertAlmostEqual(break_reminder.next_expiration.timestamp(),
                               (now_local + dt.timedelta(hours=1)).timestamp(),
                               delta=2)
        self.assertEqual(break_reminder.alert_name, "take break")
        self.assertIsNone(break_reminder.repeat_days)
        self.assertIsNone(break_reminder.repeat_frequency)
        self.assertIsNone(break_reminder.end_repeat)

        meeting_reminder = build_alert_from_intent(meeting_reminder,
                                                   AlertType.REMINDER, sea_tz)
        self.assertEqual(meeting_reminder.next_expiration.time(),
                         dt.time(hour=10))
        self.assertEqual(meeting_reminder.alert_name, "start meeting")
        self.assertIsNone(meeting_reminder.repeat_days)
        self.assertIsNone(meeting_reminder.repeat_frequency)
        self.assertIsNone(meeting_reminder.end_repeat)

        alt_dinner_reminder = build_alert_from_intent(alt_dinner_reminder,
                                                      AlertType.REMINDER,
                                                      sea_tz)
        self.assertAlmostEqual(alt_dinner_reminder.next_expiration.timestamp(),
                               (now_local + dt.timedelta(hours=3)).timestamp(),
                               delta=2)
        self.assertEqual(alt_dinner_reminder.alert_name, "start dinner")
        self.assertIsNone(alt_dinner_reminder.repeat_days)
        self.assertIsNone(alt_dinner_reminder.repeat_frequency)
        self.assertIsNone(alt_dinner_reminder.end_repeat)

        medication_reminder = build_alert_from_intent(medication_reminder,
                                                      AlertType.REMINDER,
                                                      sea_tz)
        self.assertEqual(medication_reminder.next_expiration.time(),
                         dt.time(hour=21))
        self.assertEqual(medication_reminder.alert_name, "medication")
        self.assertIsNone(medication_reminder.repeat_days)
        self.assertIsNone(medication_reminder.repeat_frequency)
        self.assertIsNone(medication_reminder.end_repeat)

        rotate_logs_reminder = build_alert_from_intent(rotate_logs_reminder,
                                                       AlertType.REMINDER,
                                                       sea_tz)
        self.assertAlmostEqual(rotate_logs_reminder.next_expiration.timestamp(),
                               (now_local + dt.timedelta(hours=8)).timestamp(),
                               delta=2)
        self.assertEqual(rotate_logs_reminder.alert_name, "rotate logs")
        self.assertIsNone(rotate_logs_reminder.repeat_days)
        self.assertEqual(rotate_logs_reminder.repeat_frequency,
                         dt.timedelta(hours=8))


class TestUIModels(unittest.TestCase):
    lingua_franca.load_language('en')

    def test_build_timer_data(self):
        from util.ui_models import build_timer_data

        now_time_valid = dt.datetime.now(dt.timezone.utc)
        invalid_alert = Alert.create(
            now_time_valid + dt.timedelta(hours=1),
            "test alert name",
            AlertType.ALARM,
            context={"testing": True}
        )

        with self.assertRaises(ValueError):
            build_timer_data(invalid_alert)

        valid_alert = Alert.create(
            dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
            "test timer",
            AlertType.TIMER,
            context={"testing": True,
                     "start_time": now_time_valid.isoformat()}
        )
        timer_data = build_timer_data(valid_alert)
        self.assertEqual(set(timer_data.keys()),
                         {'alertId', 'backgroundColor', 'expired',
                          'percentRemaining', 'timerName', 'timeDelta'})
        self.assertEqual(timer_data['alertId'], get_alert_id(valid_alert))
        self.assertAlmostEqual(timer_data['percentRemaining'], 1, 2)
        self.assertEqual(timer_data['timerName'], 'test timer')
        self.assertIsInstance(timer_data['timeDelta'], str)

        time.sleep(1)
        new_timer_data = build_timer_data(valid_alert)
        self.assertLess(new_timer_data['percentRemaining'],
                        timer_data['percentRemaining'])
        self.assertAlmostEqual(timer_data['percentRemaining'], 1, 1)

    def test_build_alarm_data(self):
        from util.ui_models import build_alarm_data
        us_context = {
            "username": "test_user",
            "user_profiles": [{
                "user": {"username": "test_user"},
                "units": {"time": 12}
            }]
        }
        metric_context = {
            "username": "test_user",
            "user_profiles": [{
                "user": {"username": "test_user"},
                "units": {"time": 24}
            }]
        }

        # Get tomorrow at 9 AM
        now_time_valid = dt.datetime.now(dt.timezone.utc)
        alarm_time = (now_time_valid +
                      dt.timedelta(hours=24)).replace(hour=9, minute=0,
                                                      second=0, microsecond=0)

        us_alarm = Alert.create(alarm_time, "Test Alarm", AlertType.ALARM,
                                context=us_context)
        metric_alarm = Alert.create(alarm_time, "Test Alarm", AlertType.ALARM,
                                    context=metric_context)

        us_display = build_alarm_data(us_alarm)
        self.assertEqual(set(us_display.keys()),
                         {'alarmTime', 'alarmAmPm', 'alarmName', 'alarmExpired',
                          'alarmIndex'})
        self.assertEqual(us_display['alarmTime'], "9:00")
        self.assertEqual(us_display['alarmAmPm'], "AM")
        self.assertEqual(us_display['alarmName'], "Test Alarm")
        self.assertFalse(us_display['alarmExpired'])
        self.assertEqual(us_display['alarmIndex'], get_alert_id(us_alarm))

        metric_display = build_alarm_data(metric_alarm)
        self.assertEqual(set(metric_display.keys()),
                         {'alarmTime', 'alarmAmPm', 'alarmName', 'alarmExpired',
                          'alarmIndex'})
        self.assertEqual(metric_display['alarmTime'], "09:00")
        self.assertEqual(metric_display['alarmAmPm'], "")
        self.assertEqual(metric_display['alarmName'], "Test Alarm")
        self.assertFalse(metric_display['alarmExpired'])
        self.assertEqual(metric_display['alarmIndex'],
                         get_alert_id(metric_alarm))


if __name__ == '__main__':
    pytest.main()
