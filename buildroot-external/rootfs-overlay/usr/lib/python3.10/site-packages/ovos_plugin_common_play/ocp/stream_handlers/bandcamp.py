from ovos_plugin_common_play.ocp.stream_handlers.youtube import \
    get_ydl_stream, YdlBackend
import enum


class BandcampBackend(str, enum.Enum):
    YDL = "youtube-dl"
    PYBANDCAMP = "pybandcamp"


def get_bandcamp_audio_stream(url, backend=BandcampBackend.PYBANDCAMP,
                              fallback=True, ydl_backend=YdlBackend.YDLP):
    try:
        if backend == BandcampBackend.PYBANDCAMP:
            return get_pybandcamp_stream(url)
        return get_ydl_stream(url, backend=ydl_backend, fallback=fallback)
    except:
        if fallback:
            if backend == BandcampBackend.PYBANDCAMP:
                return get_ydl_stream(url, backend=ydl_backend,
                                      fallback=fallback)
            return get_pybandcamp_stream(url)
        raise


def get_pybandcamp_stream(url):
    from py_bandcamp.utils import get_stream_data
    data = get_stream_data(url)
    data["uri"] = data.pop("stream")
    return data


def is_bandcamp(url):
    if not url:
        return False
    return "bandcamp." in url
