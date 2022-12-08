import requests


def get_playlist_stream(uri):
    # .pls and .m3u are not supported by gui player, parse the file
    if "pls" in uri or ".m3u" in uri:
        txt = requests.get(uri).text
        for l in txt.split("\n"):
            if l.startswith("http"):
                return {"uri": l}
    return {"uri": uri}

