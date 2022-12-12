import requests

from ovos_plugin_common_play.ocp.status import MediaType, PlaybackMode
from ovos_utils.skills.settings import PrivateSettings
from ovos_plugin_common_play.ocp.stream_handlers import YoutubeBackend, \
    BandcampBackend, YdlBackend, YoutubeLiveBackend
from dbus_next.constants import BusType


class OCPSettings(PrivateSettings):
    # media types that can be safely cast to audio only streams when GUI is
    # not available
    cast2audio = [
        MediaType.MUSIC,
        MediaType.PODCAST,
        MediaType.AUDIOBOOK,
        MediaType.RADIO,
        MediaType.RADIO_THEATRE,
        MediaType.VISUAL_STORY,
        MediaType.NEWS
    ]

    def __init__(self):
        super().__init__("ovos.common_play")

    @property
    def dbus_type(self):
        dbustype = self.get("dbus_type") or "session"
        if dbustype.lower().strip() == "system":
            return BusType.SYSTEM
        return BusType.SESSION

    @property
    def disable_mpris(self):
        return self.get("disable_mpris", False)

    @property
    def playback_mode(self):
        """class PlaybackMode(IntEnum):
        AUTO = 0 - play each entry as considered appropriate,
                   ie, make it happen the best way possible
        AUDIO_ONLY = 10  - only consider audio entries
        VIDEO_ONLY = 20  - only consider video entries
        FORCE_AUDIO = 30 - cast video to audio unconditionally
                           (audio can still play in mycroft-gui)
        FORCE_AUDIOSERVICE = 40 - cast everything to audio service backend,
                                  mycroft-gui will not be used
        EVENTS_ONLY = 50 - only emit ocp events,
                           do not display or play anything.
                           allows integration with external interfaces
        """
        return self.get("playback_mode", PlaybackMode.AUTO)

    @property
    def early_stop_thresh(self):
        """ early_stop_thresh (int): stop collecting results if we get a
                                   match with confidence >= early_stop_thresh"""
        return self.get("early_stop_thresh", 85)

    @property
    def early_stop_grace_period(self):
        """early_stop_grace_period (float): sleep this amount before early stop,
                                   allows skills that "just miss" to also be
                                   taken into account"""
        return self.get("early_stop_grace_period", 0.5)

    @property
    def backwards_compatibility(self):
        """backwards_compatibility (bool): if True emits the regular
                                            mycroft-core bus messages to get
                                            results from "old style" skills"""
        return self.get("backwards_compatibility", True)

    @property
    def allow_extensions(self):
        """  allow_extensions (bool): if True, allow skills to request more
                                     time, extend min_timeout for specific
                                     queries up to max_timeout"""
        return self.get("allow_extensions", True)

    @property
    def search_fallback(self):
        """ search_fallback (bool): if no results, perform a second query
                                   with MediaType.GENERIC"""
        return self.get("search_fallback", True)

    @property
    def force_audioservice(self):
        """
        if True play all media in audio service, DO NOT use mycroft-gui.
        Some use cases:
         - headless installs
         - setups with multiple mycroft-guis connected

         WARNING: videos may be cast to audio or filtered

              media types that can be safely cast to audio only streams
              when GUI is not available defined in self.cast2audio:

                MediaType.MUSIC
                MediaType.PODCAST
                MediaType.AUDIOBOOK
                MediaType.RADIO
                MediaType.RADIO_THEATRE
                MediaType.VISUAL_STORY
                MediaType.NEWS
        """
        return self.get("force_audioservice") or \
               self.playback_mode == PlaybackMode.FORCE_AUDIOSERVICE

    @property
    def preferred_audio_services(self):
        """ ordered list of configured audio backends,
        when OCP selects a audio service for playback this list is checked
        in order until a available backend is found
        """
        return self.get("preferred_audio_services") or \
               ["vlc", "mplayer", "simple"]

    @property
    def autoplay(self):
        """when media playback ends "click next" """
        return self.get("autoplay", True)

    @property
    def min_timeout(self):
        """min_timeout (float): minimum time to wait for skill replies,
                                 after this time, if at least 1 result was
                                 found, selection is triggered"""
        return self.get("min_timeout", 5)

    @property
    def max_timeout(self):
        """max_timeout (float): maximum time to wait for skill replies,
                                 after this time, regardless of number of
                                 results, selection is triggered"""
        return self.get("max_timeout", 15)

    @property
    def min_score(self):
        return self.get("min_score", 50)

    @property
    def audio_only(self):
        return self.playback_mode == PlaybackMode.AUDIO_ONLY

    @property
    def video_only(self):
        return self.playback_mode == PlaybackMode.VIDEO_ONLY

    @property
    def merge_search(self):
        """if True behaves as if the search results are part of the playlist
        eg:
          - click next in last track -> play next search result
          - end of playlist + autoplay -> play next search result
        """
        return self.get("merge_search", True)

    @property
    def adult_content(self):
        """by default adult content is not displayed in skills menu
        TODO:
         - split into its own UI
         - modify search results (and voice interaction) via this flag
        """
        return self.get("adult_content", False)

    @property
    def youtube_backend(self):
        """class YoutubeBackend(str, enum.Enum):
        YDL = "youtube-dl"
        PYTUBE = "pytube"
        PAFY = "pafy"
        WEBVIEW = "webview" (WIP AND BROKEN)
        INVIDIOUS = "invidious" <- default (no dependencies)
        """
        return self.get("youtube_backend") or YoutubeBackend.INVIDIOUS

    @property
    def invidious_host(self):
        """the url to the invidious instance to be used"""
        return self.get("invidious_host")

    @property
    def proxy_invidious(self):
        """get final stream locally or from where invidious is hosted
        This partially allows bypassing geoblocked content,
        but it is a global flag, not per entry.
        TODO: allow to specify per track
        """
        return self.get("invidious_proxy", False)

    @property
    def yt_chlive_backend(self):
        """class YoutubeLiveBackend(str, enum.Enum):
        PYTUBE = "pytube"
        YT_SEARCHER = "youtube_searcher"
        REDIRECT = "redirect"  <- default
            # uses youtube auto redirect https://www.youtube.com/{channel_name}/live
        YDL = "youtube-dl"
            # same as above, but always uses YoutubeBackend.YDL internally
        """
        return self.get("youtube_live_backend") or YoutubeLiveBackend.REDIRECT

    @property
    def ydl_backend(self):
        """class YdlBackend(str, enum.Enum):
        YDL = "youtube-dl"
        YDLC = "youtube-dlc"
        YDLP = "yt-dlp" <- default
        """
        return self.get("ydl_backend") or YdlBackend.YDLP

    @property
    def bandcamp_backend(self):
        """class BandcampBackend(str, enum.Enum):
        YDL = "youtube-dl"
        PYBANDCAMP = "pybandcamp"  <- default
        """
        return self.get("bandcamp_backend") or BandcampBackend.PYBANDCAMP

