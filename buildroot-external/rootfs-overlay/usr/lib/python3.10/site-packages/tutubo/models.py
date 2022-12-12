import json
from typing import List, Tuple, Optional, Iterable

from pytube import YouTube as _Yt, Channel as _Ch, Playlist as _Pl
from pytube import extract
from pytube.exceptions import VideoUnavailable
from pytube.helpers import uniqueify, cache, DeferredGeneratorList


class YoutubePreview:
    def __init__(self, renderer_data):
        self._raw_data = renderer_data


class PlaylistPreview(YoutubePreview):
    def get(self):
        return Playlist(self.playlist_url)

    @property
    def title(self):
        return self._raw_data["title"]['simpleText']

    @property
    def playlist_id(self):
        return self._raw_data["playlistId"]

    @property
    def playlist_url(self):
        return f"https://www.youtube.com/playlist?list={self.playlist_id}"

    @property
    def video_count(self):
        return self._raw_data['videoCount']

    @property
    def featured_videos(self):
        videos = []
        for v in self._raw_data['videos']:
            v = v['childVideoRenderer']
            videos.append({
                "videoId": v['videoId'],
                "url": f"https://youtube.com/watch?v={v['videoId']}",
                "image": f"https://img.youtube.com/vi/{v['videoId']}/default.jpg",
                "title": v["title"]["simpleText"]
            })
        return videos

    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return [t['thumbnails'][0] for t in self._raw_data['thumbnails']]

    def __str__(self):
        return self.title

    @property
    def as_dict(self):
        return {'playlistId': self.playlist_id,
                'title': self.title,
                'url': self.playlist_url,
                "image": self.thumbnail_url,
                'featured_videos': self.featured_videos}


class YoutubeMixPreview(PlaylistPreview):
    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return self._raw_data['thumbnail']['thumbnails']

    @property
    def as_dict(self):
        return {'playlistId': self.playlist_id,
                'title': self.title,
                'url': self.playlist_url,
                "image": self.thumbnail_url,
                'featured_videos': self.featured_videos}


class ChannelPreview(YoutubePreview):

    def get(self):
        return Channel(self.channel_url)

    @property
    def title(self):
        return self._raw_data["title"]['simpleText']

    @property
    def description(self):
        return "".join(r["text"] for r in
                       self._raw_data['descriptionSnippet']['runs'])

    @property
    def channel_id(self):
        return self._raw_data["channelId"]

    @property
    def channel_url(self):
        return f"https://www.youtube.com/channel/{self.channel_id}"

    @property
    def video_count(self):
        return int(self._raw_data['videoCountText']["runs"][0]["text"])

    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return self._raw_data['thumbnail']['thumbnails']

    def __str__(self):
        return self.title

    @property
    def as_dict(self):
        return {'channelId': self.channel_id,
                'title': self.title,
                'image': self.thumbnail_url,
                'url': self.channel_url}


class VideoPreview(YoutubePreview):

    def get(self):
        return Video(self.watch_url)

    @property
    def title(self):
        return "".join(r["text"] for r in
                       self._raw_data['title']['runs'])

    @property
    def author(self):
        return "".join(r["text"] for r in
                       self._raw_data['ownerText']['runs'])

    @property
    def channel_id(self):
        return self._raw_data['ownerText']['runs'][0][
            'navigationEndpoint']['commandMetadata'][
            'webCommandMetadata']['url']

    @property
    def channel_url(self):
        return f'https://www.youtube.com/channel/{self.channel_id}'

    @property
    def video_id(self):
        return self._raw_data['videoId']

    @property
    def watch_url(self):
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    def view_count(self):
        # Livestreams have "runs", non-livestreams have "simpleText",
        #  and scheduled releases do not have 'viewCountText'
        if 'viewCountText' in self._raw_data:
            if 'runs' in self._raw_data['viewCountText']:
                vid_view_count_text = \
                    self._raw_data['viewCountText']['runs'][0][
                        'text']
            else:
                vid_view_count_text = \
                    self._raw_data['viewCountText']['simpleText']
            # Strip ' views' text, then remove commas
            stripped_text = vid_view_count_text.split()[0].replace(
                ',', '')
            if stripped_text != 'No':
                return int(stripped_text)
        return 0

    @property
    def length(self):
        if 'lengthText' in self._raw_data:
            pts = self._raw_data['lengthText']['simpleText'].split(":")
            h, m, s = 0, 0, 0
            if len(pts) == 3:
                h, m, s = pts
            elif len(pts) == 2:
                m, s = pts
            elif len(pts) == 1:
                s = pts
            return int(s) + \
                   60 * int(m) + \
                   60 * 60 * int(h)
        return 0

    @property
    def thumbnail_url(self):
        return f"https://img.youtube.com/vi/{self.video_id}/default.jpg"

    @property
    def keywords(self):
        return []  # just for api compatibility, requires parsing url!

    def __str__(self):
        return self.title

    @property
    def as_dict(self):
        return {'length': self.length,
                'keywords': self.keywords,
                'image': self.thumbnail_url,
                'title': self.title,
                "author": self.author,
                'url': self.watch_url,
                'videoId': self.video_id}


class RelatedVideoPreview(VideoPreview):
    @property
    def as_dict(self):
        return {'length': self.length,
                'keywords': self.keywords,
                'image': self.thumbnail_url,
                'title': self.title,
                "author": self.author,
                'url': self.watch_url,
                'videoId': self.video_id}


class RelatedSearch(YoutubePreview):

    def get(self, preview=True):
        from tutubo.search import YoutubeSearch
        return YoutubeSearch(self.query, preview=preview)

    @property
    def query(self):
        return "".join(r["text"] for r in self._raw_data['query']['runs'])

    @property
    def thumbnail_url(self):
        return self.thumbnails[-1]["url"]

    @property
    def thumbnails(self):
        return self._raw_data['thumbnail']['thumbnails']

    def __str__(self):
        return self.query

    @property
    def as_dict(self):
        return {'query': self.query,
                'image': self.thumbnail_url}


class Playlist(_Pl):
    def __init__(self, url, *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self._metadata = None
        self._microformat = None

    @property
    def metadata(self):
        if self._metadata:
            return self._metadata
        else:
            self._metadata = self.initial_data['metadata'][
                'channelMetadataRenderer']
            return self._metadata

    @property
    def microformat(self):
        if self._microformat:
            return self._microformat
        else:
            self._microformat = self.initial_data['metadata'][
                'microformatDataRenderer']
            return self._microformat

    @property
    def title(self):
        """Extract playlist title

        :return: playlist title (name)
        :rtype: Optional[str]
        """
        try:
            return self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
                'title']['runs'][0]['text']
        except:  # sidebar not available
            pass
        try:
            return self.microformat['title']
        except:
            pass
        try:
            return self.metadata['title']
        except:
            pass

    @property
    def description(self) -> str:
        try:
            return self.sidebar_info[0]['playlistSidebarPrimaryInfoRenderer'][
                'description']['simpleText'].strip()
        except:  # sometimes description is an empty dict
            return ""

    @property
    def featured_videos(self):
        videos = []
        idx = 0
        for vid in self.videos:
            if idx > 5:
                break
            try:
                videos.append({
                    "videoId": vid.video_id,
                    "url": vid.watch_url,
                    "image": vid.thumbnail_url,
                    "title": vid.title
                })
                idx += 1
            except VideoUnavailable:
                continue
        return videos

    @property
    def thumbnail_url(self):
        return self.featured_videos[0]["image"]

    @property
    def as_dict(self):
        return {'playlistId': self.playlist_id,
                'title': self.title,
                'url': self.playlist_url,
                "image": self.thumbnail_url,
                'featured_videos': self.featured_videos}


class Channel(Playlist, _Ch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # see https://github.com/pytube/pytube/pull/1019
    @property
    def playlists(self) -> Iterable[Playlist]:
        """Yields Playlist objects of playlists in this channel
        :rtype: List[Playlist]
        :returns: List of Playlist
        """
        return DeferredGeneratorList(self.playlist_generator())

    @staticmethod
    def _extract_playlists(raw_json: str) -> Tuple[List[str], Optional[str]]:
        """Extracts playlists from a raw json page
        :param str raw_json: Input json extracted from the page or the last
            server response
        :rtype: Tuple[List[str], Optional[str]]
        :returns: Tuple containing a list of up to 100 video watch ids and
            a continuation token, if more videos are available
        """
        initial_data = json.loads(raw_json)

        # this is the json tree structure, if the json was extracted from
        # html
        try:
            playlists = initial_data["contents"][
                "twoColumnBrowseResultsRenderer"][
                "tabs"][2]["tabRenderer"]["content"][
                "sectionListRenderer"]["contents"][0][
                "itemSectionRenderer"]["contents"][0][
                'shelfRenderer']["content"][
                'horizontalListRenderer']["items"]
        except (KeyError, IndexError, TypeError):
            playlists = []

        continuation = None
        # remove duplicates
        return (
            uniqueify(
                list(
                    # only extract the video ids from the video data
                    map(
                        lambda x: (
                            f"/playlist?list="
                            f"{x['gridPlaylistRenderer']['playlistId']}"
                        ),
                        playlists
                    )
                ),
            ),
            continuation,
        )

    def playlist_generator(self):
        for url in self.playlist_urls:
            yield Playlist(url)

    def playlist_url_generator(self):
        """Generator that yields video URLs.
        :Yields: Video URLs
        """
        for page in self._paginate_playlists():
            for playlist in page:
                yield self._playlist_url(playlist)

    def _paginate_playlists(
            self, until_watch_id: Optional[str] = None
    ) -> Iterable[List[str]]:
        """Parse the playlist links from the page source, yields the /watch?v=
        part from video link
        :param until_watch_id Optional[str]: YouTube Video watch id until
            which the playlist should be read.
        :rtype: Iterable[List[str]]
        :returns: Iterable of lists of YouTube playlist ids
        """
        playlist_urls, continuation = self._extract_playlists(
            json.dumps(extract.initial_data(self.playlists_html))
        )
        yield playlist_urls

    @staticmethod
    def _playlist_url(playlist_path: str):
        return f"https://www.youtube.com{playlist_path}"

    @property  # type: ignore
    @cache
    def playlist_urls(self) -> DeferredGeneratorList:
        """Complete links of all the playlists in channel
        :rtype: List[str]
        :returns: List of playlist URLs
        """
        return DeferredGeneratorList(self.playlist_url_generator())

    @property
    def as_dict(self):
        return {'channelId': self.channel_id,
                'title': self.title,
                'image': self.thumbnail_url,
                'url': self.channel_url}


class Video(_Yt):
    @property
    def as_dict(self):
        return {'length': self.length,
                'keywords': self.keywords,
                'image': self.thumbnail_url,
                'title': self.title,
                "author": self.author,
                'url': self.watch_url,
                'videoId': self.video_id}


class RelatedVideo(Video):
    @property
    def as_dict(self):
        return {'length': self.length,
                'keywords': self.keywords,
                'image': self.thumbnail_url,
                'title': self.title,
                "author": self.author,
                'url': self.watch_url,
                'videoId': self.video_id}
