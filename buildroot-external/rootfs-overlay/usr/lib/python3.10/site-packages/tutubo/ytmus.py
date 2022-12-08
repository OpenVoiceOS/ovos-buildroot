import json
from tutubo.models import YoutubePreview, Video
from ytmusicapi import YTMusic


class YTMusicResult(YoutubePreview):
    @property
    def title(self):
        return self._raw_data.get("title")

    @property
    def thumbnail_url(self):
        img = self._raw_data.get("image")
        if not img and self._raw_data.get("thumbnails"):
            img = self._raw_data["thumbnails"][-1]["url"]
        return img

    @property
    def artist(self):
        artist = self._raw_data.get("artist")
        if not artist and self._raw_data.get("artists"):
            artist = ", ".join(a["name"] for a in self._raw_data['artists'])
        return artist

    @property
    def description(self):
        return self._raw_data.get("description")

    @property
    def as_dict(self):
        return self._raw_data

    def __dict__(self):
        return self.as_dict

    def __str__(self):
        return json.dumps(self.as_dict, sort_keys=True)


class MusicTrack(YTMusicResult):
    @property
    def watch_url(self):
        return "https://music.youtube.com/watch?v=" + self._raw_data["videoId"]

    @property
    def length(self):
        # converted to seconds or None
        dur = self._raw_data.get("duration")
        if isinstance(dur, str):
            dur = dur.split(":")
            if len(dur) == 2:
                m, s = dur
                return 60 * int(m) + int(s)
            elif len(dur) == 3:
                h, m, s = dur
                return 60 * 60 * int(h) + 60 * int(m) + int(s)
        return None

    @property
    def album(self):
        return self._raw_data.get("album", {}).get("name")

    @property
    def as_dict(self):
        return {"title": self.title,
                "artist": self.artist,
                "image": self.thumbnail_url,
                "url": self.watch_url,
                "duration": self.length}


class MusicVideo(MusicTrack):
    @property
    def watch_url(self):
        return "https://www.youtube.com/watch?v=" + self._raw_data["videoId"]

    def get(self):
        return Video(self.watch_url)


class MusicPlaylist(YTMusicResult):
    @property
    def tracks(self):
        if "tracks" in self._raw_data:
            return [
                MusicTrack(t) for t in self._raw_data["tracks"]
                if t.get("videoId")
            ]
        elif "songs" in self._raw_data:
            return [
                MusicTrack(t) for t in self._raw_data["songs"]["results"]
                if t.get("videoId")
            ]
        return []

    @property
    def as_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "image": self.thumbnail_url,
            "playlist": [t.as_dict for t in self.tracks]
        }


class MusicAlbum(MusicPlaylist):
    @property
    def name(self):
        return self.title


class MusicArtist(MusicPlaylist):
    @property
    def name(self):
        return self.artist

    @property
    def as_dict(self):
        return {
            "artist": self.name,
            "image": self.thumbnail_url,
            "playlist": [t.as_dict for t in self.tracks]
        }


def search_yt_music(query, as_dict=True):
    ytmusic = YTMusic()
    for r in ytmusic.search(query):
        if r["resultType"] == "video":
            if as_dict:
                yield MusicVideo(r).as_dict
            else:
                yield MusicVideo(r)
        elif r["resultType"] == "song":
            yield MusicTrack(r)
        elif r["resultType"] == "album":
            try:
                a = ytmusic.get_album(r["browseId"])
            except:
                continue
            r.update(a)
            if as_dict:
                yield MusicAlbum(r).as_dict
            else:
                yield MusicAlbum(r)
        elif r["resultType"] == "playlist":
            try:
                a = ytmusic.get_playlist(r["browseId"])
            except:
                continue
            r.update(a)
            if as_dict:
                yield MusicPlaylist(r).as_dict
            else:
                yield MusicPlaylist(r)
        elif r["resultType"] == "artist":
            try:
                a = ytmusic.get_artist(r["browseId"])
            except:
                continue
            r.update(a)
            if as_dict:
                yield MusicArtist(r).as_dict
            else:
                yield MusicArtist(r)
