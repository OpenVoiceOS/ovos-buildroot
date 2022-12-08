from ovos_plugin_manager.templates.audio import AudioBackend
from ovos_utils.log import LOG
from mycroft_bus_client.message import Message
from ovos_plugin_common_play.ocp.status import TrackState, \
    MediaState, PlayerState
import vlc
import time


VLCAudioPluginConfig = {
    "vlc": {
        "type": "ovos_vlc",
        "active": True
    }
}


class OVOSVlcService(AudioBackend):
    def __init__(self, config, bus=None, name='ovos_vlc'):
        super(OVOSVlcService, self).__init__(config, bus)
        self.instance = vlc.Instance("--no-video")

        self.player = self.instance.media_player_new()
        self._now_playing = None

        self.vlc_events = self.player.event_manager()

        self.vlc_events.event_attach(vlc.EventType.MediaPlayerPlaying,
                                     self.track_start, 1)
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerTimeChanged,
                                     self.update_playback_time, None)
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerEndReached,
                                          self.queue_ended, 0)
        self.config = config
        self.bus = bus
        self.name = name
        self.normal_volume = None
        self.low_volume = self.config.get('low_volume', 30)
        self._playback_time = 0
        self.player.audio_set_volume(100)
        self._last_sync = 0

    @property
    def playback_time(self):
        """ in milliseconds """
        return self._playback_time

    def update_playback_time(self, data, other):
        self._playback_time = data.u.new_time
        # this message is captured by ovos common play and used to sync the
        # seekbar
        if time.time() - self._last_sync > 2:
            # send event ~ every 2 s
            # the gui seems to lag a lot when sending messages too often,
            # gui expected to keep an internal fake progress bar and sync periodically
            self._last_sync = time.time()
            self.bus.emit(Message("ovos.common_play.playback_time",
                                  {"position": self._playback_time,
                                   "length": self.get_track_length()}))

    def track_start(self, data, other):
        LOG.debug('VLC playback start')
        if self._track_start_callback:
            self._track_start_callback(self.track_info().get('name'))
        self.bus.emit(Message("ovos.common_play.player.state",
                                 {"state": PlayerState.PLAYING}))
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.BUFFERING_MEDIA}))
        self.bus.emit(Message("ovos.common_play.track.state",
                              {"state": TrackState.PLAYING_AUDIOSERVICE}))

    def queue_ended(self, data, other):
        LOG.debug('VLC playback ended')
        self._now_playing = None
        if self._track_start_callback:
            self._track_start_callback(None)

        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.STOPPED}))
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.END_OF_MEDIA}))

    def supported_uris(self):
        return ['file', 'http', 'https']

    def clear_list(self):
        self.bus.emit(Message("ovos.common_play.playlist.clear"))

    def add_list(self, tracks):
        if len(tracks) >= 1:
            t = tracks[0]
            if isinstance(t, list):
                t = t[0]
            LOG.debug(f"queuing for playback: {t}")
            self._now_playing = t
            self.bus.emit(Message("ovos.common_play.track.state",
                                  {"state": TrackState.QUEUED_AUDIOSERVICE}))
            if len(tracks) > 1:
                # should never happen, means something is bypassing ovos
                # common play with bus messages
                tracks = tracks[1:]
                LOG.debug("discarded extra tracks, refused to handle "
                          "playlists in VLC, use ovos common play instead!")

    def play(self, repeat=False):
        """ Play playlist using vlc. """
        LOG.debug('VLCService Play')
        # playlist is handled in ovos common play
        # new event needed for repeat flag TODO
        if repeat: # remove log once listener is implemented in common play
            LOG.debug("ignoring repeat flag, refused to handle "
                      "playlists in VLC, use ovos common play instead!")
        track = self.instance.media_new(self._now_playing)
        self.player.set_media(track)
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.LOADED_MEDIA}))
        self.player.play()

    def stop(self):
        """ Stop vlc playback. """
        LOG.info('VLCService Stop')
        if self.player.is_playing():
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.STOPPED}))
            # Restore volume if lowered
            self.restore_volume()
            self.player.stop()
            self.clear_list()
            return True
        return False

    def pause(self):
        """ Pause vlc playback. """
        self.player.set_pause(1)
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.PAUSED}))

    def resume(self):
        """ Resume paused playback. """
        self.player.set_pause(0)
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.PLAYING}))
        self.bus.emit(Message("ovos.common_play.track.state",
                              {"state": TrackState.PLAYING_AUDIOSERVICE}))

    def next(self):
        """ Skip to next track in playlist. """
        # playlist handling done by ovos common play
        self.pause()
        self.bus.emit(Message("ovos.common_play.next"))

    def previous(self):
        """ Skip to previous track in playlist. """
        # playlist handling done by ovos common play
        self.pause()
        self.bus.emit(Message("ovos.common_play.previous"))

    def lower_volume(self):
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.duck"))

    def restore_volume(self):
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.unduck"))

    def track_info(self):
        """ Extract info of current track. """
        ret = {}
        t = self.player.get_media()
        ret['album'] = t.get_meta(vlc.Meta.Album)
        ret['artist'] = t.get_meta(vlc.Meta.Artist)
        ret['title'] = t.get_meta(vlc.Meta.Title)
        return ret

    def get_track_length(self):
        """
        getting the duration of the audio in milliseconds
        """
        return self.player.get_length()

    def get_track_position(self):
        """
        get current position in milliseconds
        """
        return self.player.get_time()

    def set_track_position(self, milliseconds):
        """
        go to position in milliseconds

          Args:
                milliseconds (int): number of milliseconds of final position
        """
        self.player.set_time(int(milliseconds))

    def seek_forward(self, seconds=1):
        """
        skip X seconds

          Args:
                seconds (int): number of seconds to seek, if negative rewind
        """
        seconds = seconds * 1000
        new_time = self.player.get_time() + seconds
        duration = self.player.get_length()
        if new_time > duration:
            new_time = duration
        self.player.set_time(new_time)

    def seek_backward(self, seconds=1):
        """
        rewind X seconds

          Args:
                seconds (int): number of seconds to seek, if negative rewind
        """
        seconds = seconds * 1000
        new_time = self.player.get_time() - seconds
        if new_time < 0:
            new_time = 0
        self.player.set_time(new_time)


def load_service(base_config, bus):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] in ["vlc", 'ovos_vlc'] and
                backends[b].get('active', False)]
    instances = [OVOSVlcService(s[1], bus, s[0]) for s in services]
    return instances
