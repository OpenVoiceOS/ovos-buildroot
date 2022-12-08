import time
from datetime import timedelta
from os.path import abspath

from mycroft_bus_client.message import Message, dig_for_message
from ovos_utils.messagebus import Message, wait_for_reply

from ovos_plugin_common_play.ocp.base import OCPAbstractComponent
from ovos_plugin_common_play.ocp.status import *


def ensure_uri(s):
    """Interprete paths as file:// uri's.

    Args:
        s: string to be checked

    Returns:
        if s is uri, s is returned otherwise file:// is prepended
    """
    if isinstance(s, str):
        if '://' not in s:
            return 'file://' + abspath(s)
        else:
            return s
    elif isinstance(s, (tuple, list)):
        if '://' not in s[0]:
            return 'file://' + abspath(s[0]), s[1]
        else:
            return s
    else:
        raise ValueError('Invalid track')


class MycroftAudioService:
    """AudioService class for interacting with the mycroft-core audio subsystem

    Args:
        bus: Mycroft messagebus connection
    """

    def __init__(self, bus):
        self.bus = bus

    @staticmethod
    def _format_msg(msg_type, msg_data=None):
        # this method ensures all skills are .forward from the utterance
        # that triggered the skill, this ensures proper routing and metadata
        msg_data = msg_data or {}
        msg = dig_for_message()
        if msg:
            msg = msg.forward(msg_type, msg_data)
        else:
            msg = Message(msg_type, msg_data)
        # at this stage source == skills, lets indicate audio service took over
        sauce = msg.context.get("source")
        if sauce == "skills":
            msg.context["source"] = "ovos.common_play"
        return msg

    def queue(self, tracks=None):
        """Queue up a track to playing playlist.

        Args:
            tracks: track uri or list of track uri's
                    Each track can be added as a tuple with (uri, mime)
                    to give a hint of the mime type to the system
        """
        tracks = tracks or []
        if isinstance(tracks, (str, tuple)):
            tracks = [tracks]
        elif not isinstance(tracks, list):
            raise ValueError
        tracks = [ensure_uri(t) for t in tracks]
        msg = self._format_msg('mycroft.audio.service.queue',
                               {'tracks': tracks})
        self.bus.emit(msg)

    def play(self, tracks=None, utterance=None, repeat=None):
        """Start playback.

        Args:
            tracks: track uri or list of track uri's
                    Each track can be added as a tuple with (uri, mime)
                    to give a hint of the mime type to the system
            utterance: forward utterance for further processing by the
                        audio service.
            repeat: if the playback should be looped
        """
        repeat = repeat or False
        tracks = tracks or []
        utterance = utterance or ''
        if isinstance(tracks, (str, tuple)):
            tracks = [tracks]
        elif not isinstance(tracks, list):
            raise ValueError
        tracks = [ensure_uri(t) for t in tracks]
        msg = self._format_msg('mycroft.audio.service.play',
                               {'tracks': tracks,
                                'utterance': utterance,
                                'repeat': repeat})
        self.bus.emit(msg)

    def stop(self):
        """Stop the track."""
        msg = self._format_msg('mycroft.audio.service.stop')
        self.bus.emit(msg)

    def next(self):
        """Change to next track."""
        msg = self._format_msg('mycroft.audio.service.next')
        self.bus.emit(msg)

    def prev(self):
        """Change to previous track."""
        msg = self._format_msg('mycroft.audio.service.prev')
        self.bus.emit(msg)

    def pause(self):
        """Pause playback."""
        msg = self._format_msg('mycroft.audio.service.pause')
        self.bus.emit(msg)

    def resume(self):
        """Resume paused playback."""
        msg = self._format_msg('mycroft.audio.service.resume')
        self.bus.emit(msg)

    def get_track_length(self):
        """
        getting the duration of the audio in seconds
        """
        length = 0
        msg = self._format_msg('mycroft.audio.service.get_track_length')
        info = self.bus.wait_for_response(msg, timeout=1)
        if info:
            length = info.data.get("length", 0)
        return length / 1000  # convert to seconds

    def get_track_position(self):
        """
        get current position in seconds
        """
        pos = 0
        msg = self._format_msg('mycroft.audio.service.get_track_position')
        info = self.bus.wait_for_response(msg, timeout=1)
        if info:
            pos = info.data.get("position", 0)
        return pos / 1000  # convert to seconds

    def set_track_position(self, seconds):
        """Seek X seconds.

        Arguments:
            seconds (int): number of seconds to seek, if negative rewind
        """
        msg = self._format_msg('mycroft.audio.service.set_track_position',
                               {"position": seconds * 1000})  # convert to ms
        self.bus.emit(msg)

    def seek(self, seconds=1):
        """Seek X seconds.

        Args:
            seconds (int): number of seconds to seek, if negative rewind
        """
        if isinstance(seconds, timedelta):
            seconds = seconds.total_seconds()
        if seconds < 0:
            self.seek_backward(abs(seconds))
        else:
            self.seek_forward(seconds)

    def seek_forward(self, seconds=1):
        """Skip ahead X seconds.

        Args:
            seconds (int): number of seconds to skip
        """
        if isinstance(seconds, timedelta):
            seconds = seconds.total_seconds()
        msg = self._format_msg('mycroft.audio.service.seek_forward',
                               {"seconds": seconds})
        self.bus.emit(msg)

    def seek_backward(self, seconds=1):
        """Rewind X seconds

         Args:
            seconds (int): number of seconds to rewind
        """
        if isinstance(seconds, timedelta):
            seconds = seconds.total_seconds()
        msg = self._format_msg('mycroft.audio.service.seek_backward',
                               {"seconds": seconds})
        self.bus.emit(msg)

    def track_info(self):
        """Request information of current playing track.

        Returns:
            Dict with track info.
        """
        msg = self._format_msg('mycroft.audio.service.track_info')
        info = self.bus.wait_for_response(
            msg, reply_type='mycroft.audio.service.track_info_reply',
            timeout=1)
        return info.data if info else {}

    def available_backends(self):
        """Return available audio backends.

        Returns:
            dict with backend names as keys
        """
        msg = self._format_msg('mycroft.audio.service.list_backends')
        response = self.bus.wait_for_response(msg)
        return response.data if response else {}

    @property
    def is_playing(self):
        """True if the audioservice is playing, else False."""
        return self.track_info() != {}


class MycroftCommonPlayInterface(OCPAbstractComponent):
    """ interface for mycroft common play """

    def __init__(self, player=None):
        super().__init__(player)
        self.query_replies = {}
        self.query_extensions = {}
        self.waiting = False
        self.start_ts = 0
        if player:
            self.bind(player)

    def bind(self, player):
        self._player = player
        self.add_event("play:query.response",
                       self.handle_cps_response)

    @property
    def cps_status(self):
        return wait_for_reply('play:status.query',
                              reply_type="play:status.response",
                              bus=self.bus).data

    def handle_cps_response(self, message):
        search_phrase = message.data["phrase"]

        if ("searching" in message.data and
                search_phrase in self.query_extensions):
            # Manage requests for time to complete searches
            skill_id = message.data["skill_id"]
            if message.data["searching"]:
                # extend the timeout by N seconds
                # IGNORED HERE, used in mycroft-playback-control skill
                if skill_id not in self.query_extensions[search_phrase]:
                    self.query_extensions[search_phrase].append(skill_id)
            else:
                # Search complete, don't wait on this skill any longer
                if skill_id in self.query_extensions[search_phrase]:
                    self.query_extensions[search_phrase].remove(skill_id)

        elif search_phrase in self.query_replies:
            # Collect all replies until the timeout
            self.query_replies[message.data["phrase"]].append(message.data)

            # forward response in OCP format
            data = self.cps2ocp(message.data)
            self.bus.emit(message.forward(
                "ovos.common_play.query.response", data))

    def send_query(self, phrase, media_type=MediaType.GENERIC):
        self.query_replies[phrase] = []
        self.query_extensions[phrase] = []
        self.bus.emit(Message('play:query', {"phrase": phrase,
                                             "question_type": media_type}))

    def get_results(self, phrase):
        if self.query_replies.get(phrase):
            return self.query_replies[phrase]
        return []

    def search(self, phrase, media_type=MediaType.GENERIC,
               timeout=5):
        self.send_query(phrase, media_type)
        self.waiting = True
        start_ts = time.time()
        while self.waiting and time.time() - start_ts <= timeout:
            time.sleep(0.2)
        self.waiting = False
        return self.get_results(phrase)

    @staticmethod
    def cps2ocp(res, media_type=MediaType.GENERIC):
        data = {
            "playback": PlaybackType.SKILL,
            "media_type": media_type,
            "is_cps": True,
            "cps_data": res['callback_data'],
            "skill_id": res["skill_id"],
            "phrase": res["phrase"],
            'match_confidence': res["conf"] * 100,
            "title": res["phrase"],
            "artist": res["skill_id"]
        }
        return {'phrase': res["phrase"],
                "is_old_style": True,
                'results': [data],
                'searching': False,
                'skill_id': res["skill_id"]}
