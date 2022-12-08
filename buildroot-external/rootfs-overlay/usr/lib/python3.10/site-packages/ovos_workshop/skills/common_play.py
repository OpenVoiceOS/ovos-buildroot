from inspect import signature
from threading import Event
from ovos_workshop.decorators.ocp import *
from ovos_workshop.skills.ovos import OVOSSkill, MycroftSkill
from mycroft_bus_client import Message
from ovos_utils.log import LOG


def get_non_properties(obj):
    """Get attibutes that are not properties from object.

    Will return members of object class along with bases down to MycroftSkill.

    Args:
        obj: object to scan

    Returns:
        Set of attributes that are not a property.
    """

    def check_class(cls):
        """Find all non-properties in a class."""
        # Current class
        d = cls.__dict__
        np = [k for k in d if not isinstance(d[k], property)]
        # Recurse through base classes excluding MycroftSkill and object
        for b in [b for b in cls.__bases__ if b not in (object, MycroftSkill)]:
            np += check_class(b)
        return np

    return set(check_class(obj.__class__))


class OVOSCommonPlaybackSkill(OVOSSkill):
    """ To integrate with the OpenVoiceOS Common Playback framework
    skills should use this base class and the companion decorators

    @ocp_search
    def ...

    @ocp_play
    def ...

    The class makes the skill available to queries from OCP and no special
    vocab for starting playback is needed.
    """

    def __init__(self, name=None, bus=None):
        super().__init__(name, bus)
        # NOTE: derived skills will likely want to override this list
        self.supported_media = [MediaType.GENERIC,
                                MediaType.AUDIO]
        self._search_handlers = []  # added via decorators
        self._featured_handlers = []  # added via decorators
        self._current_query = None
        self.__playback_handler = None
        self.__pause_handler = None
        self.__next_handler = None
        self.__prev_handler = None
        self.__resume_handler = None
        self._stop_event = Event()
        self._playing = Event()
        # TODO replace with new default
        self.skill_icon = "https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png"

    def bind(self, bus):
        """Overrides the normal bind method.

        Adds handlers for play:query and play:start messages allowing
        interaction with the playback control skill.

        This is called automatically during setup, and
        need not otherwise be used.
        """
        if bus:
            super().bind(bus)
            self.add_event('ovos.common_play.query',
                           self.__handle_ocp_query)
            self.add_event('ovos.common_play.featured_tracks.play',
                           self.__handle_ocp_featured)
            self.add_event('ovos.common_play.skills.get',
                           self.__handle_ocp_skills_get)
            self.add_event(f'ovos.common_play.{self.skill_id}.play',
                           self.__handle_ocp_play)
            self.add_event(f'ovos.common_play.{self.skill_id}.pause',
                           self.__handle_ocp_pause)
            self.add_event(f'ovos.common_play.{self.skill_id}.resume',
                           self.__handle_ocp_resume)
            self.add_event(f'ovos.common_play.{self.skill_id}.next',
                           self.__handle_ocp_next)
            self.add_event(f'ovos.common_play.{self.skill_id}.previous',
                           self.__handle_ocp_prev)
            self.add_event(f'ovos.common_play.{self.skill_id}.stop',
                           self.__handle_ocp_stop)
            self.add_event("ovos.common_play.search.stop",
                           self.__handle_stop_search)
            self.add_event("mycroft.stop",
                           self.__handle_stop_search)

    def __handle_ocp_skills_get(self, message):
        self.bus.emit(
            message.reply('ovos.common_play.announce',
                          {"skill_id": self.skill_id,
                           "skill_name": self.name,
                           "thumbnail": self.skill_icon,
                           "media_type": self.supported_media,
                           "featured_tracks": len(self._featured_handlers) >= 1}))

    def _register_decorated(self):
        # register search handlers
        for attr_name in get_non_properties(self):
            method = getattr(self, attr_name)
            if hasattr(method, 'is_ocp_search_handler'):
                if method.is_ocp_search_handler:
                    # TODO this wont accept methods with killable_event
                    #  decorators
                    self._search_handlers.append(method)
            if hasattr(method, 'is_ocp_featured_handler'):
                if method.is_ocp_featured_handler:
                    # TODO this wont accept methods with killable_event
                    #  decorators
                    self._featured_handlers.append(method)
            if hasattr(method, 'is_ocp_playback_handler'):
                if method.is_ocp_playback_handler:
                    # TODO how to handle multiple ??
                    if self.__playback_handler:
                        LOG.warning("multiple declarations of playback "
                                    "handler, replacing previous handler")
                    self.__playback_handler = method
            if hasattr(method, 'is_ocp_pause_handler'):
                if method.is_ocp_pause_handler:
                    # TODO how to handle multiple ??
                    if self.__pause_handler:
                        LOG.warning("multiple declarations of pause "
                                    "handler, replacing previous handler")
                    self.__pause_handler = method
            if hasattr(method, 'is_ocp_next_handler'):
                if method.is_ocp_next_handler:
                    # TODO how to handle multiple ??
                    if self.__next_handler:
                        LOG.warning("multiple declarations of play next "
                                    "handler, replacing previous handler")
                    self.__next_handler = method
            if hasattr(method, 'is_ocp_prev_handler'):
                if method.is_ocp_prev_handler:
                    # TODO how to handle multiple ??
                    if self.__prev_handler:
                        LOG.warning("multiple declarations of play previous "
                                    "handler, replacing previous handler")
                    self.__prev_handler = method
            if hasattr(method, 'is_ocp_resume_handler'):
                if method.is_ocp_resume_handler:
                    # TODO how to handle multiple ??
                    if self.__resume_handler:
                        LOG.warning("multiple declarations of resume playback"
                                    "handler, replacing previous handler")
                    self.__resume_handler = method
        super()._register_decorated()

        # volunteer info to OCP
        self.bus.emit(
            Message('ovos.common_play.announce',
                    {"skill_id": self.skill_id,
                     "skill_name": self.name,
                     "thumbnail": self.skill_icon,
                     "media_types": self.supported_media,
                     "featured_tracks": len(self._featured_handlers) >= 1}))

    def extend_timeout(self, timeout=0.5):
        """ request more time for searching, limits are defined by
        better-common-play framework, by default max total time is 5 seconds
        per query """
        if self._current_query:
            self.bus.emit(Message("ovos.common_play.query.response",
                                  {"phrase": self._current_query,
                                   "skill_id": self.skill_id,
                                   "skill_name": self.name,
                                   "thumbnail": self.skill_icon,
                                   "timeout": timeout,
                                   "searching": True}))

    def play_media(self, media, disambiguation=None, playlist=None):
        disambiguation = disambiguation or [media]
        playlist = playlist or [media]
        self.bus.emit(Message("ovos.common_play.play",
                              {"media": media,
                               "disambiguation": disambiguation,
                               "playlist": playlist}))

    # @killable_event("ovos.common_play.stop", react_to_stop=True)
    def __handle_ocp_play(self, message):
        if self.__playback_handler:
            self.__playback_handler(message)
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.PLAYING}))
            self._playing.set()
        else:
            LOG.error(f"Playback requested but {self.skill_id} handler not "
                      "implemented")

    def __handle_ocp_pause(self, message):
        if self.__pause_handler:
            if self.__pause_handler(message):
                self.bus.emit(Message("ovos.common_play.player.state",
                                      {"state": PlayerState.PAUSED}))
        else:
            LOG.error(f"Pause requested but {self.skill_id} handler not "
                      "implemented")

    def __handle_ocp_resume(self, message):
        if self.__resume_handler:
            if self.__resume_handler(message):
                self.bus.emit(Message("ovos.common_play.player.state",
                                      {"state": PlayerState.PLAYING}))
        else:
            LOG.error(f"Resume requested but {self.skill_id} handler not "
                      "implemented")

    def __handle_ocp_next(self, message):
        if self.__next_handler:
            self.__next_handler(message)
        else:
            LOG.error(f"Play Next requested but {self.skill_id} handler not "
                      "implemented")

    def __handle_ocp_prev(self, message):
        if self.__prev_handler:
            self.__prev_handler(message)
        else:
            LOG.error(f"Play Next requested but {self.skill_id} handler not "
                      "implemented")

    def __handle_ocp_stop(self, message):
        # for skills managing their own playback
        if self._playing.is_set():
            self.stop()
            self.gui.release()
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.STOPPED}))
            self._playing.clear()

    def __handle_stop_search(self, message):
        self._stop_event.set()

    # @killable_event("ovos.common_play.search.stop", react_to_stop=True)
    def __handle_ocp_query(self, message):
        """Query skill if it can start playback from given phrase."""
        self._stop_event.clear()
        search_phrase = message.data["phrase"]
        self._current_query = search_phrase
        media_type = message.data.get("question_type",
                                      MediaType.GENERIC)

        if media_type not in self.supported_media:
            return

        self.bus.emit(message.reply("ovos.common_play.skill.search_start",
                                    {"skill_id": self.skill_id,
                                     "skill_name": self.name,
                                     "thumbnail": self.skill_icon, }))

        # invoke the media search handlesr to let the skill perform its search
        found = False
        for handler in self._search_handlers:
            if self._stop_event.is_set():
                break
            # @ocp_search
            # def handle_search(...):
            if len(signature(handler).parameters) == 1:
                # no optional media_type argument
                results = handler(search_phrase) or []
            else:
                results = handler(search_phrase, media_type) or []

            # handler might return a generator or a list
            if isinstance(results, list):
                # inject skill id in individual results, will be needed later
                # for proper playback handling
                for idx, r in enumerate(results):
                    results[idx]["skill_id"] = self.skill_id
                self.bus.emit(message.response({"phrase": search_phrase,
                                                "skill_id": self.skill_id,
                                                "skill_name": self.name,
                                                "thumbnail": self.skill_icon,
                                                "results": results,
                                                "searching": False}))
                found = True
            else:  # generator, keeps returning results
                for r in results:
                    # inject skill id in individual results, will be needed later
                    # for proper playback handling
                    r["skill_id"] = self.skill_id
                    self.bus.emit(message.response({"phrase": search_phrase,
                                                    "skill_id": self.skill_id,
                                                    "skill_name": self.name,
                                                    "thumbnail": self.skill_icon,
                                                    "results": [r],
                                                    "searching": False}))
                    found = True
                    if self._stop_event.is_set():
                        break

        if not found:
            # Signal we are done (can't handle it)
            self.bus.emit(message.response({"phrase": search_phrase,
                                            "skill_id": self.skill_id,
                                            "skill_name": self.name,
                                            "thumbnail": self.skill_icon,
                                            "searching": False}))
        self.bus.emit(message.reply("ovos.common_play.skill.search_end",
                                    {"skill_id": self.skill_id}))

    def __handle_ocp_featured(self, message):
        skill_id = message.data["skill_id"]
        if skill_id != self.skill_id:
            return

        results = []
        for handler in self._featured_handlers:
            try:
                results += list(handler())  # handler might return a generator or a list
            except Exception as e:
                LOG.error(e)

        if not results:
            self.speak_dialog("no.media.available")
        else:
            # inject skill id in individual results
            for idx, r in enumerate(results):
                results[idx]["skill_id"] = self.skill_id
            self.bus.emit(Message("ovos.common_play.skill.play",
                                  {"skill_id": self.skill_id,
                                   "skill_name": self.name,
                                   "thumbnail": self.skill_icon,
                                   "playlist": results}))

    def default_shutdown(self):
        self.bus.emit(
            Message('ovos.common_play.skills.detach',
                    {"skill_id": self.skill_id}))
        super().default_shutdown()
