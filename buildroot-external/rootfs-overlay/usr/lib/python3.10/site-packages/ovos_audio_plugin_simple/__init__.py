import mimetypes
import re
import signal
import subprocess
from distutils.spawn import find_executable
from time import sleep

from mycroft_bus_client.message import Message
from ovos_plugin_common_play.ocp.status import TrackState, MediaState, PlayerState
from ovos_plugin_manager.templates.audio import AudioBackend
from ovos_utils.log import LOG
from requests import Session


def find_mime(path):
    mime = None
    if path.startswith('http'):
        response = Session().head(path, allow_redirects=True)
        if 200 <= response.status_code < 300:
            mime = response.headers['content-type']
    if not mime:
        mime = mimetypes.guess_type(path)[0]
    # Remove any http address arguments
    if not mime:
        mime = mimetypes.guess_type(re.sub(r'\?.*$', '', path))[0]

    if mime:
        return mime.split('/')
    else:
        return (None, None)


def play_audio(uri, play_cmd="play"):
    """ Play a audio file.

        Returns: subprocess.Popen object
    """
    play_wav_cmd = play_cmd.split() + [uri]

    try:
        return subprocess.Popen(play_wav_cmd)
    except Exception as e:
        LOG.error(f"Failed to play: {play_wav_cmd}")
        LOG.debug(f"Error: {e}")
        return None


SimpleAudioPluginConfig = {
    "simple": {
        "type": "ovos_simple",
        "active": True
    }
}


class OVOSSimpleService(AudioBackend):
    sox_play = find_executable("play")
    pulse_play = find_executable("paplay")
    alsa_play = find_executable("aplay")
    mpg123_play = find_executable("mpg123")

    def __init__(self, config, bus=None, name='ovos_simple'):
        super(OVOSSimpleService, self).__init__(config, bus)
        self.config = config
        self.bus = bus
        self.name = name

        self._now_playing = None
        self.process = None
        self._stop_signal = False
        self._is_playing = False
        self._paused = False

        self.supports_mime_hints = True
        mimetypes.init()

        self.bus.on('ovos.common_play.simple.play', self._play)

    def track_start(self, data, other):
        LOG.debug('Simple playback start')
        if self._track_start_callback:
            self._track_start_callback(self.track_info().get('name'))
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.PLAYING}))
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.BUFFERING_MEDIA}))
        self.bus.emit(Message("ovos.common_play.track.state",
                              {"state": TrackState.PLAYING_AUDIOSERVICE}))

    def queue_ended(self, data, other):
        LOG.debug('Simple playback ended')
        self._now_playing = None
        if self._track_start_callback:
            self._track_start_callback(None)

        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.STOPPED}))
        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.END_OF_MEDIA}))

    def supported_uris(self):
        uris = ['file', 'http']
        if self.sox_play:
            uris.append("https")
        return uris

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
                          "playlists in audio service, use ovos common play instead!")

    def _get_track(self, track_data):
        if isinstance(track_data, list):
            track = track_data[0]
            mime = track_data[1]
            mime = mime.split('/')
        else:  # Assume string
            track = track_data
            mime = find_mime(track)
        return track, mime

    def _is_process_running(self):
        return self.process and self.process.poll() is None

    def _stop_running_process(self):
        if self._is_process_running():
            if self._paused:
                # The child process must be "unpaused" in order to be stopped
                self.process.send_signal(signal.SIGCONT)
            self.process.terminate()
            countdown = 10
            while self._is_process_running() and countdown > 0:
                sleep(0.1)
                countdown -= 1

            if self._is_process_running():
                # Failed to shutdown when asked nicely.  Force the issue.
                LOG.debug("Killing currently playing audio...")
                self.process.kill()
        self.process = None

    def _play(self, message):
        """Implementation specific async method to handle playback.

        This allows mpg123 service to use the next method as well
        as basic play/stop.
        """
        LOG.info('SimpleAudioService._play')

        # Stop any existing audio playback
        self._stop_running_process()

        repeat = message.data.get('repeat', False)
        self._is_playing = True
        self._paused = False

        # sox should handle almost every format, but fails in some urls
        if self.sox_play:
            track = self._now_playing
            # NOTE: some urls like youtube streams will cause extension detection to fail
            # let's handle it explicitly
            ext = track.split("?")[0].split(".")[-1]
            player = self.sox_play + f" --type {ext}"

        # determine best available player
        else:
            track, mime = self._get_track(self._now_playing)
            LOG.debug(f'Mime info: {mime}')

            # wav file
            if 'wav' in mime[1]:
                player = self.pulse_play
            # guess mp3
            elif self.mpg123_play:
                player = self.mpg123_play

            # fallback to alsa, only wav files will play correctly
            player = player or self.alsa_play

        # Indicate to audio service which track is being played
        if self._track_start_callback:
            self._track_start_callback(track)

        # Replace file:// uri's with normal paths
        uri = track.replace('file://', '')

        try:
            self.process = play_audio(uri, player)
        except FileNotFoundError as e:
            LOG.error(f'Couldn\'t play audio, {e}')
            self.process = None
        except Exception as e:
            LOG.exception(repr(e))
            self.process = None

        # Wait for completion or stop request
        while (self._is_process_running() and not self._stop_signal):
            sleep(0.25)

        if self._stop_signal:
            self._stop_running_process()
            self._is_playing = False
            self._paused = False
            return
        else:
            self.process = None

        self._track_start_callback(None)
        self._is_playing = False
        self._paused = False
        self.bus.emit(Message("ovos.common_play.player.state",
                              {"state": PlayerState.STOPPED}))

    def play(self, repeat=False):
        """ Play playlist using simple. """
        LOG.debug('SimpleService Play')
        # playlist is handled in ovos common play
        # new event needed for repeat flag TODO
        if repeat:  # remove log once listener is implemented in common play
            LOG.debug("ignoring repeat flag, refused to handle "
                      "playlists in audio service, use ovos common play instead!")

        self.bus.emit(Message("ovos.common_play.media.state",
                              {"state": MediaState.LOADED_MEDIA}))
        # TODO playback
        self.bus.emit(Message('ovos.common_play.simple.play', {'repeat': repeat}))

    def stop(self):
        """ Stop simple playback. """
        LOG.info('SimpleService Stop')
        if self._is_playing:
            self._stop_signal = True
            while self._is_playing:
                sleep(0.1)
            self._stop_signal = False
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.STOPPED}))
            # Restore volume if lowered
            self.restore_volume()
            self.clear_list()
            return True
        return False

    def pause(self):
        """ Pause simple playback. """
        if self.process and not self._paused:
            # Suspend the playback process
            self.process.send_signal(signal.SIGSTOP)
            self._paused = True
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.PAUSED}))

    def resume(self):
        """ Resume paused playback. """
        if self.process and self._paused:
            # Resume the playback process
            self.process.send_signal(signal.SIGCONT)
            self._paused = False
            self.bus.emit(Message("ovos.common_play.player.state",
                                  {"state": PlayerState.PLAYING}))
            self.bus.emit(Message("ovos.common_play.track.state",
                                  {"state": TrackState.PLAYING_AUDIOSERVICE}))

    def next(self):
        """ Skip to next track in playlist. """
        self._stop_running_process()
        # playlist handling done by ovos common play
        self.bus.emit(Message("ovos.common_play.next"))

    def previous(self):
        """ Skip to previous track in playlist. """
        self._stop_running_process()
        # playlist handling done by ovos common play
        self.bus.emit(Message("ovos.common_play.previous"))

    def lower_volume(self):
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.duck"))

    def restore_volume(self):
        if self.config.get("duck", False):
            self.bus.emit(Message("ovos.common_play.unduck"))


def load_service(base_config, bus):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] in ["simple", 'ovos_simple'] and
                backends[b].get('active', False)]

    if not any([OVOSSimpleService.sox_play,
                OVOSSimpleService.pulse_play,
                OVOSSimpleService.alsa_play,
                OVOSSimpleService.mpg123_play]):
        LOG.error("No basic playback functionality detected!!")
        return []

    instances = [OVOSSimpleService(s[1], bus, s[0]) for s in services]
    return instances
