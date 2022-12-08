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

from copy import deepcopy
from typing import Optional, List
from json_database import JsonStorage
from uuid import uuid4 as uuid
from mycroft_bus_client import Message
from neon_utils.logger import LOG
from neon_utils.location_utils import to_system_time
from combo_lock import NamedLock
from ovos_utils.events import EventSchedulerInterface

from . import AlertState, AlertType
from .alert import Alert

_DEFAULT_USER = "local"


def get_alert_user(alert: Alert):
    """
    Get the user associated with the specified alert.
    :param alert: Alert object to check
    :returns: username associated with the alert or _DEFAULT_USER
    """
    return alert.context.get("username") or alert.context.get("user") \
        or _DEFAULT_USER


def get_alert_id(alert: Alert) -> Optional[str]:
    """
    Get the unique id associated with the specified alert.
    :param alert: Alert object to check
    :returns: Alert identifier if specified, else None
    """
    return alert.context.get("ident")


def sort_alerts_list(alerts: List[Alert]) -> List[Alert]:
    """
    Sort the passed list of alerts by time of next expiration,
    chronologically ascending
    :param alerts: list of Alert objects to sort
    :returns: sorted list of alerts
    """
    alerts.sort(key=lambda alert: dt.datetime.fromisoformat(
        alert.data["next_expiration_time"]))
    return alerts


def get_alerts_by_type(alerts: List[Alert]) -> dict:
    """
    Parse a list of alerts into a dict of alerts by alert type.
    :param alerts: list of Alert objects to organize
    :returns: dict of AlertType to list of alerts
    """
    sorted_dict = dict()
    for alert in AlertType:
        sorted_dict.setdefault(alert, list())
    for alert in alerts:
        key = alert.alert_type
        sorted_dict[key].append(alert)

    return sorted_dict


class AlertManager:
    def __init__(self, alerts_file: str,
                 event_scheduler: EventSchedulerInterface,
                 alert_callback: callable):
        self._alerts_store = JsonStorage(alerts_file)
        self._scheduler = event_scheduler
        self._callback = alert_callback
        self._pending_alerts = dict()
        self._missed_alerts = dict()
        self._active_alerts = dict()
        self._read_lock = NamedLock("alert_manager")
        self._active_gui_timers = list()

        self._load_cache()

    @property
    def active_gui_timers(self):
        with self._read_lock:
            return deepcopy(self._active_gui_timers)

    @property
    def missed_alerts(self):
        """
        Returns a static dict of current missed alerts
        """
        with self._read_lock:
            return deepcopy(self._missed_alerts)

    @property
    def pending_alerts(self):
        """
        Returns a static dict of current pending alerts
        """
        with self._read_lock:
            return deepcopy(self._pending_alerts)

    @property
    def active_alerts(self):
        """
        Returns a static dict of current active alerts
        """
        with self._read_lock:
            return deepcopy(self._active_alerts)

    # Query Methods
    def get_alert_status(self, alert_id: str) -> Optional[AlertState]:
        """
        Get the current state of the requested alert_id. If a repeating alert
        exists in multiple states, it will report in priority order:
        ACTIVE, MISSED, PENDING
        :param alert_id: ID of alert to query
        :returns: AlertState of the requested alert or None if alert not found
        """
        if alert_id in self._active_alerts:
            return AlertState.ACTIVE
        if alert_id in self._missed_alerts:
            return AlertState.MISSED
        if alert_id in self._pending_alerts:
            return AlertState.PENDING
        LOG.error(f"{alert_id} not found")

    def get_user_alerts(self, user: str = _DEFAULT_USER) -> dict:
        """
        Get a sorted list of alerts for the requested user.
        :param user: Username to retrieve alerts for
        :returns: dict of disposition to sorted alerts for the specified user
        """
        user = user or _DEFAULT_USER
        missed, active, pending = self._get_user_alerts(user)
        return {
            "missed": sort_alerts_list(missed),
            "active": sort_alerts_list(active),
            "pending": sort_alerts_list(pending)
        }

    def get_all_alerts(self) -> dict:
        """
        Get a sorted list of all managed alerts.
        :returns: dict of disposition to sorted alerts for all users
        """
        with self._read_lock:
            missed = sort_alerts_list([alert for alert in
                                       self._missed_alerts.values()])
            active = sort_alerts_list([alert for alert in
                                       self._active_alerts.values()])
            pending = sort_alerts_list([alert for alert in
                                        self._pending_alerts.values()])
        return {
            "missed": missed,
            "active": active,
            "pending": pending
        }

    # Alert Management
    def mark_alert_missed(self, alert_id: str):
        """
        Mark an active alert as missed
        :param alert_id: ident of active alert to mark as missed
        """
        try:
            with self._read_lock:
                self._missed_alerts[alert_id] = self._active_alerts.pop(alert_id)
            self.dismiss_alert_from_gui(alert_id)
        except KeyError:
            LOG.error(f"{alert_id} is not active")

    def dismiss_active_alert(self, alert_id: str) -> Alert:
        """
        Dismiss an active alert
        :param alert_id: ident of active alert to dismiss
        :returns: active Alert that was dismissed (None if alert_id invalid)
        """
        try:
            with self._read_lock:
                alert = self._active_alerts.pop(alert_id)
            return alert
        except KeyError:
            LOG.error(f"{alert_id} is not active")

    def snooze_alert(self, alert_id: str,
                     snooze_duration: dt.timedelta) -> Alert:
        """
        Snooze an active or missed alert for some period of time.
        :param alert_id: ID of active or missed alert to reschedule
        :param snooze_duration: time until next notification
        :returns: New Alert added to pending
        """
        alert = None
        with self._read_lock:
            if alert_id in self._active_alerts:
                alert = self._active_alerts.pop(alert_id)
            elif alert_id in self._missed_alerts:
                alert = self._missed_alerts.pop(alert_id)
        if not alert:
            raise KeyError(f'No missed or active alert with ID: {alert_id}')
        assert isinstance(alert, Alert)
        alert_dict = alert.data
        old_expiration = dt.datetime.fromisoformat(
            alert_dict['next_expiration_time'])
        new_expiration = old_expiration + snooze_duration
        alert_dict['next_expiration_time'] = new_expiration.isoformat()
        alert_dict['repeat_frequency'] = None
        alert_dict['repeat_days'] = None
        alert_dict['end_repeat'] = None
        alert_dict['alert_name'] = alert.alert_name

        if not alert_dict['context']['ident'].startswith('snoozed'):
            alert_dict['context']['ident'] = f"snoozed_{get_alert_id(alert)}"

        new_alert = Alert.from_dict(alert_dict)
        self.add_alert(new_alert)
        return new_alert

    def dismiss_missed_alert(self, alert_id: str) -> Alert:
        """
        Dismiss a missed alert
        :param alert_id: ident of active alert to dismiss
        :returns: active Alert that was dismissed (None if alert_id invalid)
        """
        try:
            with self._read_lock:
                alert = self._missed_alerts.pop(alert_id)
                self.dismiss_alert_from_gui(alert_id)
            return alert
        except KeyError:
            LOG.error(f"{alert_id} is not missed")

    def add_alert(self, alert: Alert) -> str:
        """
        Add an alert to the scheduler and return the alert ID
        :returns: string identifier for the scheduled alert
        """
        # TODO: Consider checking ident is unique
        ident = alert.context.get("ident") or str(uuid())
        self._schedule_alert_expiration(alert, ident)
        return ident

    def rm_alert(self, alert_id: str):
        """
        Remove a pending alert
        :param alert_id: ident of active alert to remove
        """
        try:
            LOG.debug(f"Removing alert: {alert_id}")
            with self._read_lock:
                self._pending_alerts.pop(alert_id)
                self.dismiss_alert_from_gui(alert_id)
        except KeyError:
            LOG.error(f"{alert_id} is not pending")
        self._scheduler.cancel_scheduled_event(alert_id)

    def add_timer_to_gui(self, alert: Alert):
        """
        Add a timer to the GUI.
        :param alert: Timer to add to GUI
        """
        self._active_gui_timers.append(alert)
        self._active_gui_timers.sort(
            key=lambda i: i.time_to_expiration.total_seconds())

    def dismiss_alert_from_gui(self, alert_id: str):
        """
        Dismiss an alert from long-lived GUI displays.
        """
        # Active timers are a copy of the original, check by ID
        for pending in self._active_gui_timers:
            if get_alert_id(pending) == alert_id:
                self._active_gui_timers.remove(pending)
                return True
        return False

    def shutdown(self):
        """
        Shutdown the Alert Manager. Mark any active alerts as missed and update
        the alerts cache on disk. Remove all events from the EventScheduler.
        """
        for alert in self.active_alerts:
            self.mark_alert_missed(alert)
            self._scheduler.cancel_scheduled_event(alert)
        for alert in self.pending_alerts:
            self._scheduler.cancel_scheduled_event(alert)
        self._dump_cache()

    def write_cache_now(self):
        """
        Write the current state of the AlertManager to file cache
        """
        self._dump_cache()

    # Alert Event Handlers
    def _schedule_alert_expiration(self, alrt: Alert, ident: str):
        """
        Schedule an event for the next expiration of the specified Alert
        :param alrt: Alert object to schedule
        :param ident: Unique identifier associated with the Alert
        """
        expire_time = alrt.next_expiration
        if not expire_time:
            raise ValueError(
                f"Requested alert has no valid expiration: {ident}")
        alrt.add_context({"ident": ident})  # Ensure ident is correct in alert
        with self._read_lock:
            self._pending_alerts[ident] = alrt
        data = alrt.data
        context = data.get("context")
        LOG.debug(f"Scheduling alert: {ident}")
        self._scheduler.schedule_event(self._handle_alert_expiration,
                                       to_system_time(expire_time),
                                       data, ident, context=context)

    def _handle_alert_expiration(self, message: Message):
        """
        Called upon expiration of an alert. Updates internal references, checks
        for repeat cases, and calls the specified callback.
        :param message: Message associated with expired alert
        """
        alert = Alert.from_dict(message.data)
        ident = message.context.get("ident")
        try:
            with self._read_lock:
                self._pending_alerts.pop(ident)
                self._active_alerts[ident] = deepcopy(alert)
        except IndexError:
            LOG.error(f"Expired alert not pending: {ident}")
        if alert.next_expiration:
            LOG.info(f"Scheduling repeating alert: {alert}")
            self._schedule_alert_expiration(alert, ident)
        self._callback(alert)

    # File Operations
    def _dump_cache(self):
        """
        Write current alerts to the cache on disk. Active alerts are not cached
        """
        with self._read_lock:
            missed_alerts = {ident: alert.serialize for
                             ident, alert in self._missed_alerts.items()}
            pending_alerts = {ident: alert.serialize for
                              ident, alert in self._pending_alerts.items()}
            self._alerts_store["missed"] = missed_alerts
            self._alerts_store["pending"] = pending_alerts
            self._alerts_store.store()

    def _load_cache(self):
        """
        Read alerts from cache on disk. Any loaded alerts will be overwritten.
        """
        # Load cached alerts into internal objects
        with self._read_lock:
            missed = self._alerts_store.get("missed") or dict()
            pending = self._alerts_store.get("pending") or dict()

        # Populate previously missed alerts
        for ident, alert_json in missed.items():
            alert = Alert.deserialize(alert_json)
            with self._read_lock:
                self._missed_alerts[ident] = alert

        # Populate previously pending alerts
        for ident, alert_json in pending.items():
            alert = Alert.deserialize(alert_json)
            if alert.is_expired:  # Alert expired while shut down
                with self._read_lock:
                    self._missed_alerts[ident] = alert
            try:
                self._schedule_alert_expiration(alert, ident)
            except ValueError:
                # Alert is expired with no valid repeat param
                pass

    # Data Operations
    def _get_user_alerts(self, user: str = _DEFAULT_USER) -> tuple:
        """
        Get all alerts for the specified user.
        :param user: Username to get alerts for
        :returns: unsorted lists of missed, active, pending alerts
        """
        with self._read_lock:
            user_missed = [alert for alert in self._missed_alerts.values() if
                           get_alert_user(alert) == user]
            user_active = [alert for alert in self._active_alerts.values() if
                           get_alert_user(alert) == user]
            user_pending = [alert for alert in self._pending_alerts.values() if
                            get_alert_user(alert) == user]
        return user_missed, user_active, user_pending
