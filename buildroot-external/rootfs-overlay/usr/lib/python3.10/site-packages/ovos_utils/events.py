import time
from datetime import datetime, timedelta
from inspect import signature

from ovos_utils.intents.intent_service_interface import to_alnum
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message, FakeBus


def unmunge_message(message, skill_id):
    """Restore message keywords by removing the Letterified skill ID.
    Args:
        message (Message): Intent result message
        skill_id (str): skill identifier
    Returns:
        Message without clear keywords
    """
    if isinstance(message, Message) and isinstance(message.data, dict):
        skill_id = to_alnum(skill_id)
        for key in list(message.data.keys()):
            if key.startswith(skill_id):
                # replace the munged key with the real one
                new_key = key[len(skill_id):]
                message.data[new_key] = message.data.pop(key)

    return message


def get_handler_name(handler):
    """Name (including class if available) of handler function.

    Args:
        handler (function): Function to be named

    Returns:
        string: handler name as string
    """
    if '__self__' in dir(handler) and 'name' in dir(handler.__self__):
        return handler.__self__.name + '.' + handler.__name__
    else:
        return handler.__name__


def create_wrapper(handler, skill_id, on_start, on_end, on_error):
    """Create the default skill handler wrapper.

    This wrapper handles things like metrics, reporting handler start/stop
    and errors.
        handler (callable): method/function to call
        skill_id: skill_id for associated skill
        on_start (function): function to call before executing the handler
        on_end (function): function to call after executing the handler
        on_error (function): function to call for error reporting
    """

    def wrapper(message):
        try:
            message = unmunge_message(message, skill_id)
            if on_start:
                on_start(message)

            if len(signature(handler).parameters) == 0:
                handler()
            else:
                handler(message)

        except Exception as e:
            if on_error:
                if len(signature(on_error).parameters) == 2:
                    on_error(e, message)
                else:
                    on_error(e)
        finally:
            if on_end:
                on_end(message)

    return wrapper


def create_basic_wrapper(handler, on_error=None):
    """Create the default skill handler wrapper.

    This wrapper handles things like metrics, reporting handler start/stop
    and errors.

    Arguments:
        handler (callable): method/function to call
        on_error (function): function to call to report error.

    Returns:
        Wrapped callable
    """

    def wrapper(message):
        try:
            if len(signature(handler).parameters) == 0:
                handler()
            else:
                handler(message)
        except Exception as e:
            if on_error:
                on_error(e)

    return wrapper


class EventContainer:
    """Container tracking messagbus handlers.

    This container tracks events added by a skill, allowing unregistering
    all events on shutdown.
    """

    def __init__(self, bus=None):
        self.bus = bus or FakeBus()
        self.events = []

    def set_bus(self, bus):
        self.bus = bus

    def add(self, name, handler, once=False):
        """Create event handler for executing intent or other event.

        Arguments:
            name (string): IntentParser name
            handler (func): Method to call
            once (bool, optional): Event handler will be removed after it has
                                   been run once.
        """

        def once_wrapper(message):
            # Remove registered one-time handler before invoking,
            # allowing them to re-schedule themselves.
            self.remove(name)
            handler(message)

        if handler:
            if once:
                self.bus.once(name, once_wrapper)
                self.events.append((name, once_wrapper))
            else:
                self.bus.on(name, handler)
                self.events.append((name, handler))

            LOG.debug('Added event: {}'.format(name))

    def remove(self, name):
        """Removes an event from bus emitter and events list.

        Args:
            name (string): Name of Intent or Scheduler Event
        Returns:
            bool: True if found and removed, False if not found
        """
        LOG.debug("Removing event {}".format(name))
        removed = False
        for _name, _handler in list(self.events):
            if name == _name:
                try:
                    self.events.remove((_name, _handler))
                except ValueError:
                    LOG.error('Failed to remove event {}'.format(name))
                    pass
                removed = True

        # Because of function wrappers, the emitter doesn't always directly
        # hold the _handler function, it sometimes holds something like
        # 'wrapper(_handler)'.  So a call like:
        #     self.bus.remove(_name, _handler)
        # will not find it, leaving an event handler with that name left behind
        # waiting to fire if it is ever re-installed and triggered.
        # Remove all handlers with the given name, regardless of handler.
        if removed:
            self.bus.remove_all_listeners(name)
        return removed

    def __iter__(self):
        return iter(self.events)

    def clear(self):
        """Unregister all registered handlers and clear the list of registered
        events.
        """
        for e, f in self.events:
            self.bus.remove(e, f)
        self.events = []  # Remove reference to wrappers


class EventSchedulerInterface:
    """Interface for accessing the event scheduler over the message bus."""

    def __init__(self, name, sched_id=None, bus=None):
        self.name = name
        self.sched_id = sched_id
        self.bus = bus or FakeBus()
        self.events = EventContainer(bus)

        self.scheduled_repeats = []

    def set_bus(self, bus):
        self.bus = bus
        self.events.set_bus(bus)

    def set_id(self, sched_id):
        self.sched_id = sched_id

    def _create_unique_name(self, name):
        """Return a name unique to this skill using the format
        [skill_id]:[name].

        Arguments:
            name:   Name to use internally

        Returns:
            str: name unique to this skill
        """
        return str(self.sched_id) + ':' + (name or '')

    def _schedule_event(self, handler, when, data, name,
                        repeat_interval=None, context=None):
        """Underlying method for schedule_event and schedule_repeating_event.

        Takes scheduling information and sends it off on the message bus.

        Arguments:
            handler:                method to be called
            when (datetime):        time (in system timezone) for first
                                    calling the handler, or None to
                                    initially trigger <frequency> seconds
                                    from now
            data (dict, optional):  data to send when the handler is called
            name (str, optional):   reference name, must be unique
            repeat_interval (float/int):  time in seconds between calls
            context (dict, optional): message context to send
                                      when the handler is called
        """
        if isinstance(when, (int, float)) and when >= 0:
            when = datetime.now() + timedelta(seconds=when)
        if not name:
            name = self.name + handler.__name__
        unique_name = self._create_unique_name(name)
        if repeat_interval:
            self.scheduled_repeats.append(name)  # store "friendly name"

        data = data or {}

        def on_error(e):
            LOG.exception('An error occured executing the scheduled event '
                          '{}'.format(repr(e)))

        wrapped = create_basic_wrapper(handler, on_error)
        self.events.add(unique_name, wrapped, once=not repeat_interval)
        event_data = {'time': time.mktime(when.timetuple()),
                      'event': unique_name,
                      'repeat': repeat_interval,
                      'data': data}
        self.bus.emit(Message('mycroft.scheduler.schedule_event',
                              data=event_data, context=context))

    def schedule_event(self, handler, when, data=None, name=None,
                       context=None):
        """Schedule a single-shot event.

        Arguments:
            handler:               method to be called
            when (datetime/int/float):   datetime (in system timezone) or
                                   number of seconds in the future when the
                                   handler should be called
            data (dict, optional): data to send when the handler is called
            name (str, optional):  reference name
                                   NOTE: This will not warn or replace a
                                   previously scheduled event of the same
                                   name.
            context (dict, optional): message context to send
                                      when the handler is called
        """
        self._schedule_event(handler, when, data, name, context=context)

    def schedule_repeating_event(self, handler, when, interval,
                                 data=None, name=None, context=None):
        """Schedule a repeating event.

        Arguments:
            handler:                method to be called
            when (datetime):        time (in system timezone) for first
                                    calling the handler, or None to
                                    initially trigger <frequency> seconds
                                    from now
            interval (float/int):   time in seconds between calls
            data (dict, optional):  data to send when the handler is called
            name (str, optional):   reference name, must be unique
            context (dict, optional): message context to send
                                      when the handler is called
        """
        # Do not schedule if this event is already scheduled by the skill
        if name not in self.scheduled_repeats:
            # If only interval is given set to trigger in [interval] seconds
            # from now.
            if not when:
                when = datetime.now() + timedelta(seconds=interval)
            self._schedule_event(handler, when, data, name, interval,
                                 context=context)
        else:
            LOG.debug('The event is already scheduled, cancel previous '
                      'event if this scheduling should replace the last.')

    def update_scheduled_event(self, name, data=None):
        """Change data of event.

        Arguments:
            name (str): reference name of event (from original scheduling)
        """
        data = data or {}
        data = {
            'event': self._create_unique_name(name),
            'data': data
        }
        self.bus.emit(Message('mycroft.schedule.update_event',
                              data=data))

    def cancel_scheduled_event(self, name):
        """Cancel a pending event. The event will no longer be scheduled
        to be executed

        Arguments:
            name (str): reference name of event (from original scheduling)
        """
        unique_name = self._create_unique_name(name)
        data = {'event': unique_name}
        if name in self.scheduled_repeats:
            self.scheduled_repeats.remove(name)
        if self.events.remove(unique_name):
            self.bus.emit(Message('mycroft.scheduler.remove_event',
                                  data=data))

    def get_scheduled_event_status(self, name):
        """Get scheduled event data and return the amount of time left

        Arguments:
            name (str): reference name of event (from original scheduling)

        Returns:
            int: the time left in seconds

        Raises:
            Exception: Raised if event is not found
        """
        event_name = self._create_unique_name(name)
        data = {'name': event_name}

        reply_name = 'mycroft.event_status.callback.{}'.format(event_name)
        msg = Message('mycroft.scheduler.get_event', data=data)
        status = self.bus.wait_for_response(msg, reply_type=reply_name)

        if status:
            event_time = int(status.data[0][0])
            current_time = int(time.time())
            time_left_in_seconds = event_time - current_time
            LOG.info(time_left_in_seconds)
            return time_left_in_seconds
        else:
            raise Exception("Event Status Messagebus Timeout")

    def cancel_all_repeating_events(self):
        """Cancel any repeating events started by the skill."""
        # NOTE: Gotta make a copy of the list due to the removes that happen
        #       in cancel_scheduled_event().
        for e in list(self.scheduled_repeats):
            self.cancel_scheduled_event(e)

    def shutdown(self):
        """Shutdown the interface unregistering any event handlers."""
        self.cancel_all_repeating_events()
        self.events.clear()
