import mimetypes

from ovos_plugin_common_play.ocp.stream_handlers.bandcamp import *
from ovos_plugin_common_play.ocp.stream_handlers.deezer import *
from ovos_plugin_common_play.ocp.stream_handlers.rssfeeds import *
from ovos_plugin_common_play.ocp.stream_handlers.youtube import *
from ovos_plugin_common_play.ocp.stream_handlers.playlists import *


def find_mime(uri):
    """ Determine mime type. """
    mime = mimetypes.guess_type(uri)
    if mime:
        return mime
    else:
        return None


def is_ydl_available():
    try:
        try:
            import youtube_dl
        except:
            try:
                import youtube_dlc
            except:
                import yt_dlp
        return True
    except:
        return False


def is_youtube_available():
    try:
        try:
            import pytube
        except:
            import pafy
        return True
    except:
        return is_ydl_available()


def is_ytchlive_available():
    try:
        try:
            import pytube
        except:
            import youtube_searcher
        return True
    except:
        return False


def is_deezer_available():
    try:
        import deezeridu
        return True
    except:
        return False


def is_rss_available():
    try:
        import feedparser
        return True
    except:
        return False


def is_bandcamp_available():
    try:
        import py_bandcamp
        return True
    except:
        return False


def available_extractors():
    ext = ["/", "http"]
    if is_deezer_available():
        ext.append("deezer//")
    if is_rss_available():
        ext.append("rss//")
    if is_ydl_available():
        ext.append("ydl//")
    if is_youtube_available():
        ext.append("youtube//")
    if is_ytchlive_available():
        ext.append("youtube.channel.live//")
    if is_bandcamp_available():
        ext.append("bandcamp//")
    return ext
