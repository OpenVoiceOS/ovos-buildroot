import random
from os.path import join, dirname
from time import sleep

from ovos_utils.gui import is_gui_connected, is_gui_running
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message
from ovos_config import Configuration

from ovos_plugin_common_play.ocp.gui import OCPMediaPlayerGUI
from ovos_plugin_common_play.ocp.media import Playlist, MediaEntry, NowPlaying
from ovos_plugin_common_play.ocp.mpris import MprisPlayerCtl
from ovos_plugin_common_play.ocp.search import OCPSearch
from ovos_plugin_common_play.ocp.settings import OCPSettings
from ovos_plugin_common_play.ocp.status import *
from ovos_plugin_common_play.ocp.mycroft_cps import MycroftAudioService
from ovos_workshop import OVOSAbstractApplication


class OCPMediaPlayer(OVOSAbstractApplication):
    def __init__(self, bus=None, settings=None, lang=None, gui=None,
                 resources_dir=None):
        settings = settings or OCPSettings()
        resources_dir = resources_dir or join(dirname(__file__), "res")
        gui = gui or OCPMediaPlayerGUI()
        # mpris settings
        manage_players = settings.get("manage_external_players", False)
        if settings.disable_mpris:
            LOG.info("MPRIS integration is disabled")
            self.mpris = None
        else:
            self.mpris = MprisPlayerCtl(manage_players=manage_players)

        self.state = PlayerState.STOPPED
        self.loop_state = LoopState.NONE
        self.media_state = MediaState.NO_MEDIA
        self.playlist = Playlist()
        self.shuffle = False
        self.now_playing = NowPlaying()
        self.media = OCPSearch()
        self.audio_service = None
        self._audio_backend = None
        self.track_history = {}
        super().__init__("ovos_common_play", settings=settings, bus=bus,
                         gui=gui, resources_dir=resources_dir, lang=lang)

    def bind(self, bus=None):
        super(OCPMediaPlayer, self).bind(bus)
        self.now_playing.bind(self)
        self.media.bind(self)
        self.gui.bind(self)
        if self.mpris:
            self.mpris.bind(self)
        self.audio_service = MycroftAudioService(self.bus)
        self.register_bus_handlers()

    def register_bus_handlers(self):
        # audio ducking TODO improve to wait for end of speech ?
        self.add_event('recognizer_loop:record_begin',
                       self.handle_duck_request)
        self.add_event('recognizer_loop:record_end',
                       self.handle_unduck_request)

        # mycroft-gui media service
        self.add_event('gui.player.media.service.sync.status',
                       self.handle_player_state_update)
        self.add_event("gui.player.media.service.get.next",
                       self.handle_next_request)
        self.add_event("gui.player.media.service.get.previous",
                       self.handle_prev_request)
        self.add_event("gui.player.media.service.get.repeat",
                       self.handle_repeat_toggle_request)
        self.add_event("gui.player.media.service.get.shuffle",
                       self.handle_shuffle_toggle_request)

        # ovos common play bus api
        self.add_event('ovos.common_play.player.state',
                       self.handle_player_state_update)
        self.add_event('ovos.common_play.media.state',
                       self.handle_player_media_update)
        self.add_event('ovos.common_play.play',
                       self.handle_play_request)
        self.add_event('ovos.common_play.pause',
                       self.handle_pause_request)
        self.add_event('ovos.common_play.resume',
                       self.handle_resume_request)
        self.add_event('ovos.common_play.stop',
                       self.handle_stop_request)
        self.add_event('ovos.common_play.next',
                       self.handle_next_request)
        self.add_event('ovos.common_play.previous',
                       self.handle_prev_request)
        self.add_event('ovos.common_play.seek',
                       self.handle_seek_request)
        self.add_event('ovos.common_play.get_track_length',
                       self.handle_track_length_request)
        self.add_event('ovos.common_play.set_track_position',
                       self.handle_set_track_position_request)
        self.add_event('ovos.common_play.get_track_position',
                       self.handle_track_position_request)
        self.add_event('ovos.common_play.track_info',
                       self.handle_track_info_request)
        self.add_event('ovos.common_play.list_backends',
                       self.handle_list_backends_request)
        self.add_event('ovos.common_play.playlist.set',
                       self.handle_playlist_set_request)
        self.add_event('ovos.common_play.playlist.clear',
                       self.handle_playlist_clear_request)
        self.add_event('ovos.common_play.playlist.queue',
                       self.handle_playlist_queue_request)
        self.add_event('ovos.common_play.duck',
                       self.handle_duck_request)
        self.add_event('ovos.common_play.unduck',
                       self.handle_unduck_request)
        self.add_event('ovos.common_play.shuffle.set',
                       self.handle_set_shuffle)
        self.add_event('ovos.common_play.shuffle.unset',
                       self.handle_unset_shuffle)
        self.add_event('ovos.common_play.repeat.set',
                       self.handle_set_repeat)
        self.add_event('ovos.common_play.repeat.unset',
                       self.handle_unset_repeat)

    @property
    def active_skill(self):
        return self.now_playing.skill_id

    @property
    def active_backend(self):
        return self.now_playing.playback

    @property
    def tracks(self):
        return self.playlist.entries

    @property
    def disambiguation(self):
        return self.media.search_playlist.entries

    @property
    def can_prev(self):
        if self.active_backend != PlaybackType.MPRIS and \
                self.playlist.is_first_track:
            return False
        return True

    @property
    def can_next(self):
        if self.loop_state != LoopState.NONE or \
                self.shuffle or \
                self.active_backend == PlaybackType.MPRIS:
            return True
        elif self.settings.merge_search and \
                not self.media.search_playlist.is_last_track:
            return True
        elif not self.playlist.is_last_track:
            return True
        return False

    # state
    def set_media_state(self, state):
        if state == self.media_state:
            return
        self.media_state = state
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": self.media_state}))

    def set_player_state(self, state):
        if state == self.state:
            return
        self.state = state
        state2str = {PlayerState.PLAYING: "Playing", PlayerState.PAUSED: "Paused", PlayerState.STOPPED: "Stopped"}
        self.gui["status"] = state2str[self.state]
        if self.mpris:
            self.mpris.update_props({"CanPause": self.state == PlayerState.PLAYING,
                                     "CanPlay": self.state == PlayerState.PAUSED,
                                     "PlaybackStatus": state2str[state]})
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": self.state}))

    def set_now_playing(self, track):
        """ Currently playing media """
        if (isinstance(track, dict) and track.get("uri")) or \
                (isinstance(track, MediaEntry) and track.uri):
            # single track entry (dict)
            self.now_playing.update(track)
            # copy now_playing (without event handlers) to playlist
            entry = self.now_playing.as_entry()
            if entry not in self.playlist:  # compared by uri
                self.playlist.add_entry(entry)
        else:
            # this is a playlist result (list of dicts)
            if isinstance(track, MediaEntry):
                pl = track.data.get("playlist")
            else:
                pl = track.get("playlist") or track.get("data", {}).get("playlist")
            if pl:
                self.playlist.clear()
                for entry in pl:
                    self.playlist.add_entry(entry)

            if len(self.playlist):
                self.now_playing.update(self.playlist[0])
            else:
                self.now_playing.update(track)

        # sync playlist position
        self.playlist.goto_track(self.now_playing)

        # update gui values
        self.gui.update_current_track()
        self.gui.update_playlist()
        if self.mpris:
            self.mpris.update_props(
                {"Metadata": self.now_playing.mpris_metadata}
            )

    # stream handling
    def validate_stream(self):
        if self.now_playing.is_cps:
            self.now_playing.playback = PlaybackType.SKILL

        if self.active_backend not in [PlaybackType.SKILL,
                                       PlaybackType.UNDEFINED,
                                       PlaybackType.MPRIS]:
            try:
                self.now_playing.extract_stream()
            except Exception as e:
                LOG.exception(e)
                return False
            has_gui = is_gui_running() or is_gui_connected(self.bus)
            if not has_gui or self.settings.force_audioservice:
                # No gui, so lets force playback to use audio only
                self.now_playing.playback = PlaybackType.AUDIO_SERVICE
            self.gui["stream"] = self.now_playing.uri

        self.gui.update_current_track()
        return True

    def on_invalid_media(self):
        self.gui.show_playback_error()
        self.play_next()

    # media controls
    def play_media(self, track, disambiguation=None, playlist=None):
        if self.mpris:
            self.mpris.stop()
        if self.state == PlayerState.PLAYING:
            self.pause()  # make it more responsive
        if disambiguation:
            self.media.search_playlist.replace(disambiguation)
            self.media.search_playlist.sort_by_conf()
            self.gui.update_search_results()
        if playlist:
            self.playlist.replace(playlist)
        if track in self.playlist:
            self.playlist.goto_track(track)
        self.set_now_playing(track)
        self.play()

    @property
    def audio_service_player(self):
        if not self._audio_backend:
            self._audio_backend = self._get_prefered_audio_backend()
        return self._audio_backend

    def _get_prefered_audio_backend(self):
        # NOTE - the bus api tells us what backends are loaded
        # however it does not provide "type", so we need to get that from config
        # we still hit the messagebus to account for loading failures,
        # even if config claims backend is enabled it might not load
        backends = self.audio_service.available_backends()
        cfg = Configuration()["Audio"]["backends"]
        available = [k for k, v in backends.items()
                     if cfg[k].get("type", "") != "ovos_common_play"]
        for b in self.settings.preferred_audio_services:
            if b in available:
                return b
        LOG.error("Preferred audio service backend not installed")
        return "simple"

    def play(self):
        # stop any external media players
        if self.mpris:
            self.mpris.stop()
        # validate new stream
        # TODO buffering animation ?
        if not self.validate_stream():
            # TODO error animation
            self.on_invalid_media()
            return
        self.gui.show_player()

        if self.now_playing.uri not in self.track_history:
            self.track_history[self.now_playing.uri] = 0
        self.track_history[self.now_playing.uri] += 1

        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.AUDIO_SERVICE]:
            LOG.debug("Requesting playback: PlaybackType.AUDIO")
            if self.active_backend == PlaybackType.AUDIO_SERVICE:
                # we explicitly want to use a audio backend for audio only output
                self.audio_service.play(self.now_playing.uri,
                                        utterance=self.audio_service_player)
                self.bus.emit(Message("ovos.common_play.track.state", {
                    "state": TrackState.PLAYING_AUDIOSERVICE}))
                self.set_player_state(PlayerState.PLAYING)
            elif is_gui_running():
                # handle audio natively in mycroft-gui
                sleep(2) # wait for gui page to start or this is sent before page
                self.bus.emit(Message("gui.player.media.service.play", {
                    "track": self.now_playing.uri,
                    "mime": self.now_playing.mimetype,
                    "repeat": False}))
                sleep(0.2) # wait for the above message to be processed
                self.bus.emit(Message("ovos.common_play.track.state", {
                    "state": TrackState.PLAYING_AUDIO}))
        elif self.active_backend == PlaybackType.SKILL:
            LOG.debug("Requesting playback: PlaybackType.SKILL")
            if self.now_playing.is_cps:  # mycroft-core compat layer
                LOG.debug("     - Mycroft common play result selected")
                self.bus.emit(Message('play:start',
                                      {"skill_id": self.now_playing.skill_id,
                                       "callback_data": self.now_playing.cps_data,
                                       "phrase": self.now_playing.phrase}))
            else:
                self.bus.emit(Message(
                    f'ovos.common_play.{self.now_playing.skill_id}.play',
                    self.now_playing.info))
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_SKILL}))
        elif self.active_backend == PlaybackType.VIDEO:
            LOG.debug("Requesting playback: PlaybackType.VIDEO")
            # handle video natively in mycroft-gui
            self.bus.emit(Message("gui.player.media.service.play", {
                "track": self.now_playing.uri,
                "mime": self.now_playing.mimetype,
                "repeat": False}))
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_VIDEO}))
        elif self.active_backend == PlaybackType.WEBVIEW:
            LOG.debug("Requesting playback: PlaybackType.WEBVIEW")
            # open a url in native webview in mycroft-gui
            self.bus.emit(Message("ovos.common_play.track.state", {
                "state": TrackState.PLAYING_WEBVIEW}))
        else:
            raise ValueError("invalid playback request")
        if self.mpris:
            self.mpris.update_props({"CanGoNext": self.can_next})
            self.mpris.update_props({"CanGoPrevious": self.can_prev})

    def play_shuffle(self):
        LOG.debug("Shuffle == True")
        if len(self.playlist) > 1 and not self.playlist.is_last_track:
            self.playlist.set_position(random.randint(0, len(self.playlist)))
            self.set_now_playing(self.playlist.current_track)
        else:
            self.media.search_playlist.next_track()
            self.set_now_playing(self.media.search_playlist.current_track)

    def play_next(self):
        if self.active_backend in [PlaybackType.MPRIS]:
            if self.mpris:
                self.mpris.play_next()
            return
        elif self.active_backend in [PlaybackType.SKILL, PlaybackType.UNDEFINED]:
            self.bus.emit(Message(f'ovos.common_play.{self.now_playing.skill_id}.next'))
            return
        self.pause()  # make more responsive

        if self.loop_state == LoopState.REPEAT_TRACK:
            self.play()
        elif self.shuffle:
            self.play_shuffle()
        elif not self.playlist.is_last_track:
            self.playlist.next_track()
            self.set_now_playing(self.playlist.current_track)
            LOG.info(f"Next track index: {self.playlist.position}")
        elif not self.media.search_playlist.is_last_track and \
                self.settings.merge_search:
            while self.media.search_playlist.current_track in self.playlist:
                self.media.search_playlist.next_track()
            self.set_now_playing(self.media.search_playlist.current_track)
            LOG.info(f"Next search index: {self.media.search_playlist.position}")
        else:
            if self.loop_state == LoopState.REPEAT and len(self.playlist):
                LOG.debug("end of playlist, repeat == True")
                self.playlist.set_position(0)
            else:
                LOG.info("requested next, but there aren't any more tracks")
                self.gui.handle_end_of_playback()
                return
        self.play()

    def play_prev(self):
        if self.active_backend in [PlaybackType.MPRIS]:
            if self.mpris:
                self.mpris.play_prev()
            return
        elif self.active_backend in [PlaybackType.SKILL, PlaybackType.UNDEFINED]:
            self.bus.emit(Message(f'ovos.common_play.{self.now_playing.skill_id}.prev'))
            return
        self.pause()  # make more responsive

        if self.shuffle:
            self.play_shuffle()
        elif not self.playlist.is_first_track:
            self.playlist.prev_track()
            self.set_now_playing(self.playlist.current_track)
            LOG.debug(f"Previous track index: {self.playlist.position}")
            self.play()
        else:
            LOG.debug("requested previous, but already in 1st track")

    def pause(self):
        LOG.debug(f"Pausing playback: {self.active_backend}")
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.audio_service.pause()
        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.VIDEO,
                                   PlaybackType.UNDEFINED]:
            self.bus.emit(Message("gui.player.media.service.pause"))
        if self.active_backend in [PlaybackType.SKILL,
                                   PlaybackType.UNDEFINED]:
            self.bus.emit(Message(f'ovos.common_play'
                                  f'.{self.active_skill}.pause'))
        if self.active_backend in [PlaybackType.MPRIS] and self.mpris:
            self.mpris.pause()
        self.set_player_state(PlayerState.PAUSED)

    def resume(self):
        LOG.debug(f"Resuming playback: {self.active_backend}")
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.audio_service.resume()

        if self.active_backend in [PlaybackType.SKILL,
                                   PlaybackType.UNDEFINED]:
            self.bus.emit(
                Message(f'ovos.common_play.{self.active_skill}.resume'))

        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.VIDEO]:
            self.bus.emit(Message('gui.player.media.service.resume'))

        if self.active_backend in [PlaybackType.MPRIS] and self.mpris:
            self.mpris.resume()

        self.set_player_state(PlayerState.PLAYING)

    def seek(self, position):
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.audio_service.set_track_position(position / 1000)
        self.gui["position"] = position

    def stop(self):
        # stop any search still happening
        self.bus.emit(Message("ovos.common_play.search.stop"))

        LOG.debug("Stopping playback")
        if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                   PlaybackType.UNDEFINED]:
            self.stop_audio_service()
            self.set_player_state(PlayerState.STOPPED)
        if self.active_backend in [PlaybackType.SKILL,
                                   PlaybackType.UNDEFINED]:
            self.stop_audio_skill()
        if self.active_backend in [PlaybackType.AUDIO,
                                   PlaybackType.VIDEO,
                                   PlaybackType.UNDEFINED]:
            self.stop_gui_player()
            self.set_player_state(PlayerState.STOPPED)
        #if self.active_backend in [PlaybackType.MPRIS] and self.mpris:
        #    self.mpris.stop()

    def stop_gui_player(self):
        self.bus.emit(Message("gui.player.media.service.stop"))

    def stop_audio_skill(self):
        self.bus.emit(Message(f'ovos.common_play.{self.active_skill}.stop'))

    def stop_audio_service(self):
        self.audio_service.stop()

    def reset(self):
        self.stop()
        self.playlist.clear()
        self.media.clear()
        self.set_media_state(MediaState.NO_MEDIA)
        self.shuffle = False
        self.loop_state = LoopState.NONE

    def shutdown(self):
        self.stop()
        if self.mpris:
            self.mpris.shutdown()
        self.now_playing.shutdown()
        self.gui.shutdown()
        self.media.shutdown()
        self.remove_event('recognizer_loop:record_begin')
        self.remove_event('recognizer_loop:record_end')
        self.remove_event('gui.player.media.service.sync.status')
        self.remove_event("gui.player.media.service.get.next")
        self.remove_event("gui.player.media.service.get.previous")

    # player -> common play
    def handle_player_state_update(self, message):
        state = message.data.get("state")
        if state == self.state:
            return
        for k in PlayerState:
            if k == state:
                LOG.info(f"PlayerState changed: {repr(k)}")
        if state == PlayerState.PLAYING:
            self.state = PlayerState.PLAYING
        elif state == PlayerState.PAUSED:
            self.state = PlayerState.PAUSED
        elif state == PlayerState.STOPPED:
            self.state = PlayerState.STOPPED

        if self.mpris:
            state2str = {PlayerState.PLAYING: "Playing",
                         PlayerState.PAUSED: "Paused",
                         PlayerState.STOPPED: "Stopped"}
            self.mpris.update_props({"CanPause": state == PlayerState.PLAYING,
                                     "CanPlay": state == PlayerState.PAUSED,
                                     "PlaybackStatus": state2str[state]})

    def handle_player_media_update(self, message):
        state = message.data.get("state")
        if state == self.media_state:
            return
        for k in MediaState:
            if k == state:
                LOG.info(f"MediaState changed: {repr(k)}")
        self.media_state = state
        if state == MediaState.END_OF_MEDIA:
            self.handle_playback_ended(message)
        elif state == MediaState.INVALID_MEDIA:
            self.handle_invalid_media(message)
            if self.settings.autoplay:
                self.play_next()

    def handle_invalid_media(self, message):
        self.gui.show_playback_error()

    def handle_playback_ended(self, message):
        LOG.debug("Playback ended")
        if self.settings.autoplay and \
                self.active_backend != PlaybackType.MPRIS:
            self.play_next()
            return

        self.gui.handle_end_of_playback(message)

    # ovos common play bus api requests
    def handle_play_request(self, message):
        LOG.debug("Received external OVOS playback request")
        repeat = message.data.get("repeat", False)
        if repeat:
            self.loop_state = LoopState.REPEAT

        if message.data.get("tracks"):
            # backwards compat / old style
            playlist = disambiguation = message.data["tracks"]
            media = playlist[0]
        else:
            media = message.data.get("media")
            playlist = message.data.get("playlist") or [media]
            disambiguation = message.data.get("disambiguation") or [media]
        self.play_media(media, disambiguation, playlist)

    def handle_pause_request(self, message):
        self.pause()

    def handle_stop_request(self, message):
        self.stop()

    def handle_resume_request(self, message):
        self.resume()

    def handle_seek_request(self, message):
        # from bus api
        miliseconds = message.data.get("seconds", 0) * 1000

        # from audio player GUI
        position = message.data.get("seekValue")
        if not position:
            position = self.now_playing.position or 0
            if self.active_backend in [PlaybackType.AUDIO_SERVICE,
                                       PlaybackType.UNDEFINED]:
                position = self.audio_service.get_track_position() or position
            position += miliseconds
        self.seek(position)

    def handle_next_request(self, message):
        self.play_next()

    def handle_prev_request(self, message):
        self.play_prev()

    def handle_set_shuffle(self, message):
        self.shuffle = True
        self.gui.update_seekbar_capabilities()

    def handle_unset_shuffle(self, message):
        self.shuffle = False
        self.gui.update_seekbar_capabilities()

    def handle_set_repeat(self, message):
        self.loop_state = LoopState.REPEAT
        self.gui.update_seekbar_capabilities()

    def handle_unset_repeat(self, message):
        self.loop_state = LoopState.NONE
        self.gui.update_seekbar_capabilities()

    # playlist control bus api
    def handle_repeat_toggle_request(self, message):
        if self.loop_state == LoopState.REPEAT_TRACK:
            self.loop_state = LoopState.NONE
        elif self.loop_state == LoopState.REPEAT:
            self.loop_state = LoopState.REPEAT_TRACK
        elif self.loop_state == LoopState.NONE:
            self.loop_state = LoopState.REPEAT
        LOG.info(f"Repeat: {self.loop_state}")
        self.gui.update_seekbar_capabilities()

    def handle_shuffle_toggle_request(self, message):
        self.shuffle = not self.shuffle
        LOG.info(f"Shuffle: {self.shuffle}")
        self.gui.update_seekbar_capabilities()

    def handle_playlist_set_request(self, message):
        self.playlist.clear()
        self.handle_playlist_queue_request(message)

    def handle_playlist_queue_request(self, message):
        for track in message.data["tracks"]:
            self.playlist.add_entry(track)
        self.gui.update_playlist()

    def handle_playlist_clear_request(self, message):
        self.playlist.clear()
        self.set_media_state(MediaState.NO_MEDIA)
        self.gui.update_playlist()

    # audio ducking
    def handle_duck_request(self, message):
        if self.state == PlayerState.PLAYING:
            self.pause()

    def handle_unduck_request(self, message):
        if self.state == PlayerState.PAUSED:
            self.resume()

    # track data
    def handle_track_length_request(self, message):
        l = self.now_playing.length
        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            l = self.audio_service.get_track_length() or l
        data = {"length": l}
        self.bus.emit(message.response(data))

    def handle_track_position_request(self, message):
        pos = self.now_playing.position
        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            pos = self.audio_service.get_track_position() or pos
        data = {"position": pos}
        self.bus.emit(message.response(data))

    def handle_set_track_position_request(self, message):
        miliseconds = message.data.get("position")
        self.seek(miliseconds)

    def handle_track_info_request(self, message):
        data = self.now_playing.as_dict
        if self.active_backend == PlaybackType.AUDIO_SERVICE:
            data = self.audio_service.track_info() or data
        self.bus.emit(message.response(data))

    # internal info
    def handle_list_backends_request(self, message):
        data = self.audio_service.available_backends()
        self.bus.emit(message.response(data))
