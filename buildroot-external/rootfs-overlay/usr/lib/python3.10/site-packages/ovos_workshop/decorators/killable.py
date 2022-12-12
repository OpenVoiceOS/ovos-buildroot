import time
from ovos_utils import create_killable_daemon
from ovos_utils.messagebus import Message
import threading
from inspect import signature
from functools import wraps


class AbortEvent(StopIteration):
    """ abort bus event handler """


class AbortIntent(AbortEvent):
    """ abort intent parsing """


class AbortQuestion(AbortEvent):
    """ gracefully abort get_response queries """


def killable_intent(msg="mycroft.skills.abort_execution",
                    callback=None, react_to_stop=True, call_stop=True,
                    stop_tts=True):
    return killable_event(msg, AbortIntent, callback, react_to_stop,
                          call_stop, stop_tts)


def killable_event(msg="mycroft.skills.abort_execution", exc=AbortEvent,
                   callback=None, react_to_stop=False, call_stop=False,
                   stop_tts=False):
    # Begin wrapper
    def create_killable(func):

        @wraps(func)
        def call_function(*args, **kwargs):
            skill = args[0]
            t = create_killable_daemon(func, args, kwargs, autostart=False)

            def abort(_):
                if not t.is_alive():
                    return
                if stop_tts:
                    skill.bus.emit(Message("mycroft.audio.speech.stop"))
                if call_stop:
                    # call stop on parent skill
                    skill.stop()

                # ensure no orphan get_response daemons
                # this is the only killable daemon that core itself will
                # create, users should also account for this condition with
                # callbacks if using the decorator for other purposes
                skill._handle_killed_wait_response()

                try:
                    while t.is_alive():
                        t.raise_exc(exc)
                        time.sleep(0.1)
                except threading.ThreadError:
                    pass  # already killed
                except AssertionError:
                    pass  # could not determine thread id ?
                if callback is not None:
                    if len(signature(callback).parameters) == 1:
                        # class method, needs self
                        callback(skill)
                    else:
                        callback()

            # save reference to threads so they can be killed later
            skill._threads.append(t)
            skill.bus.once(msg, abort)
            if react_to_stop:
                skill.bus.once(skill.skill_id + ".stop", abort)
            t.start()
            return t

        return call_function

    return create_killable

