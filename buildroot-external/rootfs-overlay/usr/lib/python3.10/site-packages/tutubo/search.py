import enum

from pytube.contrib.search import Search as _Search
from tutubo.models import *
from tutubo.ytmus import *


class SearchType(enum.IntEnum):
    YOUTUBE = enum.auto()
    VIDEOS = enum.auto()
    RELATED_VIDEOS = enum.auto()
    CHANNELS = enum.auto()
    PLAYLISTS = enum.auto()
    YOUTUBE_MIX = enum.auto()
    RELATED_QUERIES = enum.auto()

    MUSIC = enum.auto()
    MUSIC_TRACK = enum.auto()
    MUSIC_VIDEO = enum.auto()
    MUSIC_ARTIST = enum.auto()
    MUSIC_PLAYLIST = enum.auto()
    MUSIC_ALBUM = enum.auto()

    ALL = enum.auto()


class YoutubeSearch(_Search):
    def __init__(self, query, preview=True, thumbnail_url=""):
        super().__init__(query)
        self.preview = preview
        self.thumbnail_url = thumbnail_url

    @property
    def as_dict(self):
        return {'query': self.query,
                'image': self.thumbnail_url}

    # pytube extensions - TODO https://github.com/pytube/pytube/pull/1133
    def iterate_youtube(self, max_res=-1, search_type=SearchType.YOUTUBE):
        idx = 0
        for r in self._iterate_and_parse(search_type=search_type):
            idx += 1
            if 0 < max_res < idx:
                break
            if not self.preview:
                r = r.get()
            yield r

    def _iterate_and_parse(self, continuation=None,
                           search_type=SearchType.ALL):
        """Fetch from the innertube API and parse the results.

        :param str continuation:
            Continuation string for fetching results.
        :rtype: tuple
        :returns:
            A tuple of a list of YouTube objects and a continuation string.
        """
        # Begin by executing the query and identifying the relevant sections
        #  of the results
        raw_results = self.fetch_query(continuation)

        # Initial result is handled by try block, continuations by except block
        try:
            sections = \
                raw_results['contents']['twoColumnSearchResultsRenderer'][
                    'primaryContents']['sectionListRenderer']['contents']
        except KeyError:
            sections = raw_results['onResponseReceivedCommands'][0][
                'appendContinuationItemsAction']['continuationItems']
        item_renderer = None
        continuation_renderer = None
        for s in sections:
            if 'itemSectionRenderer' in s:
                item_renderer = s['itemSectionRenderer']
            if 'continuationItemRenderer' in s:
                continuation_renderer = s['continuationItemRenderer']

        # If the continuationItemRenderer doesn't exist, assume no further results
        if continuation_renderer:
            next_continuation = continuation_renderer['continuationEndpoint'][
                'continuationCommand']['token']
        else:
            next_continuation = None

        # If the itemSectionRenderer doesn't exist, assume no results.
        if item_renderer:
            raw_video_list = item_renderer['contents']
            for video_details in raw_video_list:
                # Skip over ads
                if video_details.get('searchPyvRenderer', {}).get('ads', None):
                    continue

                # Skip "recommended" type videos e.g. "people also watched" and "popular X"
                #  that break up the search results
                elif 'shelfRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.YOUTUBE,
                                        SearchType.RELATED_VIDEOS]:
                    for v in video_details['shelfRenderer']['content'][
                        'verticalListRenderer']['items']:
                        yield RelatedVideoPreview(v['videoRenderer'])
                    continue

                # Skip auto-generated "mix" playlist results
                elif 'radioRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.YOUTUBE,
                                        SearchType.YOUTUBE_MIX]:
                    yield YoutubeMixPreview(video_details['radioRenderer'])
                    continue

                # Skip playlist results
                elif 'playlistRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.YOUTUBE,
                                        SearchType.PLAYLISTS]:
                    yield PlaylistPreview(video_details['playlistRenderer'])
                    continue

                # Skip channel results
                elif 'channelRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.YOUTUBE,
                                        SearchType.CHANNELS]:
                    yield ChannelPreview(video_details['channelRenderer'])
                    continue

                # Skip 'people also searched for' results
                elif 'horizontalCardListRenderer' in video_details and \
                        search_type in [SearchType.RELATED_QUERIES,
                                        SearchType.YOUTUBE,
                                        SearchType.ALL]:
                    for v in video_details['horizontalCardListRenderer'][
                        'cards']:
                        yield RelatedSearch(v['searchRefinementCardRenderer'])
                    continue

                # Can't seem to reproduce, probably related to typo fix suggestions
                elif 'didYouMeanRenderer' in video_details:
                    continue

                # Seems to be the renderer used for the image shown on a no results page
                elif 'backgroundPromoRenderer' in video_details:
                    continue

                # no more results
                elif 'messageRenderer' in video_details:
                    return

                elif 'videoRenderer' in video_details and \
                        search_type in [SearchType.ALL,
                                        SearchType.YOUTUBE,
                                        SearchType.VIDEOS]:
                    yield VideoPreview(video_details['videoRenderer'])

        if next_continuation:
            for r in self._iterate_and_parse(next_continuation, search_type):
                yield r

    def iterate_videos(self, max_res=-1):
        for v in self.iterate_youtube(max_res):
            if isinstance(v, Video) or isinstance(v, VideoPreview):
                yield v

    def iterate_related_videos(self, max_res=-1):
        for v in self.iterate_youtube(max_res):
            if isinstance(v, RelatedVideo):
                yield v

    def iterate_channels(self, max_res=-1):
        for v in self.iterate_youtube(max_res):
            if isinstance(v, Channel) or isinstance(v, ChannelPreview):
                yield v

    def iterate_playlists(self, max_res=-1):
        for v in self.iterate_youtube(max_res):
            if isinstance(v, PlaylistPreview) or isinstance(v, Playlist):
                yield v

    def iterate_mixes(self, max_res=-1):
        for v in self.iterate_youtube(max_res):
            if isinstance(v, YoutubeMixPreview):
                yield v

    def iterate_queries(self, max_res=-1):
        for v in self.iterate_youtube(max_res):
            if isinstance(v, RelatedSearch):
                yield v

    # youtube music
    def iterate_youtube_music(self, search_type=SearchType.MUSIC):
        ytmusic = YTMusic()
        for r in ytmusic.search(self.query):
            if r["resultType"] == "video" and \
                    search_type in [SearchType.MUSIC,
                                    SearchType.ALL,
                                    SearchType.MUSIC_VIDEO]:
                yield MusicVideo(r)
            elif r["resultType"] == "song" and \
                    search_type in [SearchType.MUSIC,
                                    SearchType.ALL,
                                    SearchType.MUSIC_TRACK]:
                yield MusicTrack(r)
            elif r["resultType"] == "album" and \
                    search_type in [SearchType.MUSIC,
                                    SearchType.ALL,
                                    SearchType.MUSIC_ALBUM]:
                try:
                    a = ytmusic.get_album(r["browseId"])
                except:
                    continue
                r.update(a)
                yield MusicAlbum(r)
            elif r["resultType"] == "playlist" and \
                    search_type in [SearchType.MUSIC,
                                    SearchType.ALL,
                                    SearchType.MUSIC_PLAYLIST]:
                try:
                    a = ytmusic.get_playlist(r["browseId"])
                except:
                    continue
                r.update(a)
                yield MusicPlaylist(r)
            elif r["resultType"] == "artist" and \
                    search_type in [SearchType.MUSIC,
                                    SearchType.MUSIC_ARTIST,
                                    SearchType.ALL]:
                try:
                    a = ytmusic.get_artist(r["browseId"])
                except:
                    continue
                r.update(a)
                yield MusicArtist(r)

    def iterate_music_albums(self, max_res=-1):
        n = 0
        for v in self.iterate_youtube_music(SearchType.MUSIC_ALBUM):
            yield v
            n += 1
            if n > max_res:
                break

    def iterate_music_artists(self, max_res=-1):
        n = 0
        for v in self.iterate_youtube_music(SearchType.MUSIC_ARTIST):
            yield v
            n += 1
            if n > max_res:
                break

    def iterate_music_tracks(self, max_res=-1):
        n = 0
        for v in self.iterate_youtube_music(SearchType.MUSIC_TRACK):
            yield v
            n += 1
            if n > max_res:
                break

    def iterate_music_playlists(self, max_res=-1):
        n = 0
        for v in self.iterate_youtube_music(SearchType.MUSIC_PLAYLIST):
            yield v
            n += 1
            if n > max_res:
                break

    def iterate_music_videos(self, max_res=-1):
        n = 0
        for v in self.iterate_youtube_music(SearchType.MUSIC_VIDEO):
            yield v
            n += 1
            if n > max_res:
                break


def search_yt(query, as_dict=True, parse=False, max_res=50):
    s = YoutubeSearch(query, preview=not parse)
    for v in s.iterate_youtube(max_res=max_res):
        if as_dict:
            yield v.as_dict
        else:
            yield v
