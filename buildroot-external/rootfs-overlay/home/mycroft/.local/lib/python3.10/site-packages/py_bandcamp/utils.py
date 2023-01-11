import json

from py_bandcamp.session import SESSION as requests


def extract_blob(url, params=None):
    blob = requests.get(url, params=params).text
    for b in blob.split("data-blob='")[1:]:
        json_blob = b.split("'")[0]
        return json.loads(json_blob)
    for b in blob.split("data-blob=\"")[1:]:
        json_blob = b.split("\"")[0].replace("&quot;", '"')
        return json.loads(json_blob)


def extract_ldjson_blob(url, clean=False):
    txt_string = requests.get(url).text

    json_blob = txt_string. \
        split('<script type="application/ld+json">')[-1]. \
        split("</script>")[0]

    data = json.loads(json_blob)

    def _clean_list(l):
        for idx, v in enumerate(l):
            if isinstance(v, dict):
                l[idx] = _clean_dict(v)
            if isinstance(v, list):
                l[idx] = _clean_list(v)
        return l

    def _clean_dict(d):
        clean = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = _clean_dict(v)
            if isinstance(v, list):
                v = _clean_list(v)
            k = k.replace("@", "")
            clean[k] = v
        return clean

    if clean:
        return _clean_dict(data)
    return data


def get_props(d, props=None):
    props = props or []
    data = {}
    for p in d['additionalProperty']:
        if p['name'] in props or not props:
            data[p['name']] = p['value']
    return data


def get_stream_data(url):
    data = extract_ldjson_blob(url)
    artist_data = data['byArtist']
    album_data = data['inAlbum']
    kws = data["keywords"]
    if isinstance(kws, str):
        kws = kws.split(", ")
    result = {
        "categories": data["@type"],
        'album_name': album_data['name'],
        'artist': artist_data['name'],
        'image': data['image'],
        "title": data['name'],
        "url": url,
        "tags": kws + data.get("tags", [])
    }
    for p in data['additionalProperty']:
        if p['name'] == 'file_mp3-128':
            result["stream"] = p["value"]
    return result
