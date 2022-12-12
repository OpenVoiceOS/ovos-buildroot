from ovos_plugin_common_play.ocp.status import *
from ovos_plugin_common_play.ocp.stream_handlers import is_youtube, \
    get_deezer_audio_stream, get_rss_first_stream, \
    get_youtube_live_from_channel, find_mime, get_bandcamp_audio_stream, \
    get_ydl_stream, get_youtube_stream, get_playlist_stream, YoutubeBackend
from ovos_utils.json_helper import merge_dict
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message
from os.path import join, dirname
from dbus_next.service import Variant


# TODO subclass from dict (?)
class MediaEntry:
    def __init__(self, title="", uri="", skill_id="ovos.common_play",
                 image=None, match_confidence=0,
                 playback=PlaybackType.UNDEFINED,
                 status=TrackState.DISAMBIGUATION, phrase=None,
                 position=0, length=None, bg_image=None, skill_icon=None,
                 artist=None, is_cps=False, cps_data=None, javascript="",
                 **kwargs):
        self.match_confidence = match_confidence
        self.title = title
        self.uri = uri
        self.artist = artist
        self.skill_id = skill_id
        self.status = status
        self.playback = playback
        self.image = image or join(dirname(__file__), "res/ui/images/ocp_bg.png")
        self.position = position
        self.phrase = phrase
        self.length = length  # None -> live stream
        self.skill_icon = skill_icon or join(dirname(__file__), "res/ui/images/ocp.png")
        self.bg_image = bg_image or join(dirname(__file__), "res/ui/images/ocp_bg.png")
        self.is_cps = is_cps
        self.data = kwargs
        self.cps_data = cps_data or {}
        self.javascript = javascript  # custom code to run in Webview after page load

    def update(self, entry, skipkeys=None, newonly=False):
        skipkeys = skipkeys or []
        if isinstance(entry, MediaEntry):
            entry = entry.as_dict
        for k, v in entry.items():
            if k not in skipkeys and hasattr(self, k):
                if newonly and self.__getattribute__(k):
                    # skip, do not replace existing values
                    continue
                self.__setattr__(k, v)

    @staticmethod
    def from_dict(data):
        if data.get("bg_image") and data["bg_image"].startswith("/"):
            data["bg_image"] = "file:/" + data["bg_image"]
        data["skill"] = data.get("skill_id") or "ovos.common_play"
        data["position"] = data.get("position", 0)
        data["length"] = data.get("length") or \
                         data.get("track_length") or \
                         data.get("duration")  # or get_duration_from_url(url)
        data["skill_icon"] = data.get("skill_icon") or data.get("skill_logo")
        data["status"] = data.get("status") or TrackState.DISAMBIGUATION
        data["playback"] = data.get("playback", PlaybackType.UNDEFINED)
        data["uri"] = data.get("stream") or data.get("uri") or data.get("url")
        data["title"] = data.get("title") or data["uri"]
        data["artist"] = data.get("artist") or data.get("author")
        data["is_cps"] = data.get("is_old_style") or data.get("is_cps", False)
        data["cps_data"] = data.get("cps_data") or {}
        return MediaEntry(**data)

    @property
    def info(self):
        # media results / playlist QML data model
        return merge_dict(self.as_dict, self.infocard)

    @property
    def infocard(self):
        return {
            "duration": self.length,
            "track": self.title,
            "image": self.image,
            "album": self.skill_id,
            "source": self.skill_icon,
            "uri": self.uri
        }

    @property
    def mpris_metadata(self):
        meta = {"xesam:url": Variant('s', self.uri)}
        if self.artist:
            meta['xesam:artist'] = Variant('as', [self.artist])
        if self.title:
            meta['xesam:title'] = Variant('s', self.title)
        if self.image:
            meta['mpris:artUrl'] = Variant('s', self.image)
        if self.length:
            meta['mpris:length'] = Variant('d', self.length)
        return meta

    @property
    def as_dict(self):
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith("_")}

    @property
    def mimetype(self):
        if self.uri:
            return find_mime(self.uri)

    def __eq__(self, other):
        if isinstance(other, MediaEntry):
            other = other.infocard
        # dict compatison
        return other == self.infocard

    def __repr__(self):
        return str(self.as_dict)

    def __str__(self):
        return str(self.as_dict)


class Playlist(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._position = 0

    @property
    def position(self):
        return self._position

    def goto_start(self):
        self._position = 0

    def clear(self) -> None:
        super(Playlist, self).clear()
        self._position = 0

    @property
    def entries(self):
        entries = []
        for e in self:
            if isinstance(e, dict):
                e = MediaEntry.from_dict(e)
            if isinstance(e, MediaEntry):
                entries.append(e)
        return entries

    def sort_by_conf(self):
        self.sort(key=lambda k: k.match_confidence \
            if isinstance(k, MediaEntry) else \
            k.get("match_confidence", 0), reverse=True)

    def add_entry(self, entry, index=-1):
        assert isinstance(index, int)
        if isinstance(entry, dict):
            entry = MediaEntry.from_dict(entry)
        assert isinstance(entry, MediaEntry)
        if index == -1:
            index = len(self)

        if index < self.position:
            self.set_position(self.position + 1)

        self.insert(index, entry)

    def remove_entry(self, entry):
        if isinstance(entry, int):
            self.pop(entry)
            return
        if isinstance(entry, dict):
            entry = MediaEntry.from_dict(entry)
        assert isinstance(entry, MediaEntry)
        for idx, e in self.entries:
            if e == entry:
                self.pop(idx)
                break
        else:
            raise ValueError("entry not in playlist")

    def replace(self, new_list):
        self.clear()
        for e in new_list:
            self.add_entry(e)

    def __contains__(self, item):
        if isinstance(item, dict):
            item = MediaEntry.from_dict(item)
        if not isinstance(item, MediaEntry):
            return False
        for e in self.entries:
            if not e.uri and e.data.get("playlist"):
                if e.title == item.title and not item.uri:
                    return True
                # track in playlist
                for t in e.data["playlist"]:
                    if t.get("uri") == item.uri:
                        return True
            elif e.uri == item.uri:
                return True
        return False

    def _validate_position(self):
        if len(self) and (self.position >= len(self) or self.position < 0):
            LOG.error("Playlist pointer is in an invalid position! Going to "
                      "start of playlist")
            self._position = 0

    def set_position(self, idx):
        self._position = idx
        self._validate_position()

    @property
    def is_first_track(self):
        if len(self) == 0:
            return True
        return self.position == 0

    @property
    def is_last_track(self):
        if len(self) == 0:
            return True
        return self.position == len(self) - 1

    def goto_track(self, track):
        if isinstance(track, MediaEntry):
            uri = track.uri
        else:
            uri = track.get("uri", "")
        for idx, t in enumerate(self):
            if isinstance(t, MediaEntry):
                uri2 = t.uri
            else:
                uri2 = t.get("uri", "")
            if uri == uri2:
                self.set_position(idx)
                LOG.debug(f"New playlist position: {self.position}")
                return

    @property
    def current_track(self):
        if len(self) == 0:
            return None
        self._validate_position()
        return self[self.position]

    def next_track(self):
        self.set_position(self.position + 1)

    def prev_track(self):
        self.set_position(self.position - 1)


class NowPlaying(MediaEntry):
    @property
    def bus(self):
        return self._player.bus

    @property
    def _settings(self):
        return self._player.settings

    def as_entry(self):
        return MediaEntry.from_dict(self.as_dict)

    def bind(self, player):
        # needs to start with _ to avoid json serialization errors
        self._player = player
        self._player.add_event("ovos.common_play.track.state",
                               self.handle_track_state_change)
        self._player.add_event("ovos.common_play.playback_time",
                               self.handle_sync_seekbar)
        self._player.add_event('gui.player.media.service.get.meta',
                               self.handle_player_metadata_request)
        self._player.add_event('mycroft.audio.service.track_info_reply',
                               self.handle_sync_trackinfo)
        self._player.add_event('mycroft.audio.service.play',
                               self.handle_audio_service_play)
        self._player.add_event('mycroft.audio.playing_track',
                               self.handle_audio_service_play_start)

    def shutdown(self):
        self._player.remove_event("ovos.common_play.track.state")
        self._player.remove_event("ovos.common_play.playback_time")
        self._player.remove_event('gui.player.media.service.get.meta')
        self._player.remove_event('mycroft.audio_only.service.track_info_reply')

    def update(self, entry, skipkeys=None, newonly=False):
        super().update(entry, skipkeys, newonly)
        # uri updates should not be skipped
        if newonly and entry.get("uri"):
            super().update({"uri": entry["uri"]})
        # sync with gui media player on track change
        self.bus.emit(Message("gui.player.media.service.set.meta",
                              {"title": self.title,
                               "image": self.image,
                               "artist": self.artist}))

    def extract_stream(self):
        uri = self.uri
        if self.playback == PlaybackType.VIDEO:
            video = True
        else:
            video = False
        meta = {}
        if uri.startswith("rss//"):
            uri = uri.replace("rss//", "")
            meta = get_rss_first_stream(uri)
            if not meta:
                LOG.error("RSS feed stream extraction failed!!!")

        if uri.startswith("bandcamp//"):
            uri = uri.replace("bandcamp//", "")
            meta = get_bandcamp_audio_stream(
                uri, backend=self._settings.bandcamp_backend,
                ydl_backend=self._settings.ydl_backend)
            if not meta:
                LOG.error("bandcamp stream extraction failed!!!")

        if uri.startswith("deezer//"):
            uri = uri.replace("deezer//", "")
            meta = get_deezer_audio_stream(uri)
            if not meta:
                LOG.error("deezer stream extraction failed!!!")
            else:
                LOG.debug(f"deezer cache: {meta['uri']}")

        elif uri.startswith("youtube.channel.live//"):
            uri = uri.replace("youtube.channel.live//", "")
            uri = get_youtube_live_from_channel(
                uri, ocp_settings=self._settings)["url"]
            if not uri:
                LOG.error("youtube channel live stream extraction failed!!!")
            else:
                uri = "youtube//" + uri

        if uri.startswith("ydl//"):
            # supports more than youtube!!!
            uri = uri.replace("ydl//", "")
            meta = get_ydl_stream(uri, ocp_settings=self._settings)
            if not meta:
                LOG.error("ydl stream extraction failed!!!")

        elif uri.startswith("youtube//") or is_youtube(uri):
            uri = uri.replace("youtube//", "")
            if self._settings.youtube_backend == YoutubeBackend.WEBVIEW:
                self.playback = meta["playback"] = PlaybackType.WEBVIEW

            if self.playback != PlaybackType.WEBVIEW:
                meta = get_youtube_stream(
                    uri, audio_only=not video, ocp_settings=self._settings)

            if not meta and self.playback != PlaybackType.WEBVIEW:
                LOG.error("youtube stream extraction failed!!!")
                LOG.warning("Forcing webview playback")
                self.playback = meta["playback"] = PlaybackType.WEBVIEW

            if self.playback == PlaybackType.WEBVIEW:
                vid_id = uri.split("v=")[-1].split("&")[0]
                uri = f"https://{self._settings.invidious_host}/watch?v={vid_id}"

        # .pls and .m3u are not supported by gui player, parse the file
        if "pls" in uri or "m3u" in uri:
            meta = get_playlist_stream(uri)

        meta = meta or {"uri": uri}

        # update media entry with new data
        self.update(meta, newonly=True)

    # events from gui_player/audio_service
    def handle_player_metadata_request(self, message):
        self.bus.emit(message.reply("gui.player.media.service.set.meta",
                                    {"title": self.title,
                                     "image": self.image,
                                     "artist": self.artist}))

    def handle_track_state_change(self, message):
        status = message.data["state"]
        self.status = status
        for k in TrackState:
            if k == status:
                LOG.info(f"TrackState changed: {repr(k)}")

        if status == TrackState.PLAYING_SKILL:
            # skill is handling playback internally
            pass
        elif status == TrackState.PLAYING_AUDIOSERVICE:
            # audio service is handling playback
            pass
        elif status == TrackState.PLAYING_VIDEO:
            # ovos common play is handling playback in GUI
            pass
        elif status == TrackState.PLAYING_AUDIO:
            # ovos common play is handling playback in GUI
            pass

        elif status == TrackState.DISAMBIGUATION:
            # alternative results # TODO its this 1 track or a list ?
            pass
        elif status in [TrackState.QUEUED_SKILL,
                        TrackState.QUEUED_VIDEO,
                        TrackState.QUEUED_AUDIOSERVICE]:
            # audio service is handling playback and this is in playlist
            pass

    def handle_sync_seekbar(self, message):
        """ event sent by ovos audio backend plugins """
        self.length = message.data["length"]
        self.position = message.data["position"]

    def handle_sync_trackinfo(self, message):
        self.update(message.data)

    def handle_audio_service_play(self, message):
        tracks = message.data.get("tracks") or []
        # only present in ovos-core
        skill_id = message.context.get("skill_id") or 'mycroft.audio_interface'
        for idx, track in enumerate(tracks):
            # TODO try to extract metadata from uri (latency ?)
            if idx == 0:
                self.update(
                    {"uri": track,
                     "title": track.split("/")[-1],
                     "status": TrackState.QUEUED_AUDIOSERVICE,
                     'skill_id': skill_id,
                     "playback": PlaybackType.AUDIO_SERVICE}
                )
            else:
                # TODO sync playlist ?
                pass

    def handle_audio_service_play_start(self, message):
        self.update(
            {"status": TrackState.PLAYING_AUDIOSERVICE,
             "playback": PlaybackType.AUDIO_SERVICE})


