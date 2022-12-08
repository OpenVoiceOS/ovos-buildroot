from os import makedirs
from os.path import join
from tempfile import gettempdir

from ovos_utils.log import LOG


def get_deezer_audio_stream(url, deezer=None, path=None):
    try:
        import deezeridu
    except ImportError:
        LOG.error("can not extract deezer stream, deezeridu is not available")
        LOG.info("pip install deezeridu")
        raise

    path = path or join(gettempdir(), "deezer")
    makedirs(path, exist_ok=True)

    try:
        deezer = deezer or deezeridu.Deezer()
        t = deezer.download(url, output_dir=path, recursive_quality=True)
        track_info = t.track_info
        track_info["uri"] = "file://" + t.song_path
        track_info["image"] = "file://" + t.image_path
        return track_info
    except Exception as e:
        LOG.error(e)
        return {}


def is_deezer(url):
    if not url:
        return False
    return "deezer." in url
