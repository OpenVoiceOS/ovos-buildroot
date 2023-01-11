#!/usr/bin/python3

from datetime import datetime
from os import makedirs
from os.path import (
	isdir, basename, join
)
from urllib.parse import urlparse
from zipfile import ZipFile, ZIP_DEFLATED

from requests import get as req_get

from .settings import header
from .exceptions import InvalidLink


def link_is_valid(link):
    netloc = urlparse(link).netloc

    if not any(
            c_link == netloc
            for c_link in ["www.deezer.com", "deezer.com", "deezer.page.link"]
    ):
        raise InvalidLink(link)


def get_ids(link):
    parsed = urlparse(link)
    path = parsed.path
    ids = path.split("/")[-1]
    return ids


def request(url):
    thing = req_get(url, headers=header)
    return thing


def artist_sort(array):
    if len(array) > 1:
        for a in array:
            for b in array:
                if a in b and a != b:
                    array.remove(b)

    array = list(
        dict.fromkeys(array)
    )

    artists = " & ".join(array)
    return artists


def __check_dir(directory):
    if not isdir(directory):
        makedirs(directory)


def check_track_md5(infos: dict):
    if "FALLBACK" in infos:
        song_md5 = infos['FALLBACK']['MD5_ORIGIN']
        version = infos['FALLBACK']['MEDIA_VERSION']
    else:
        song_md5 = infos['MD5_ORIGIN']
        version = infos['MEDIA_VERSION']

    return song_md5, version


def check_track_token(infos: dict):
    if "FALLBACK" in infos:
        track_token = infos['FALLBACK']['TRACK_TOKEN']
    else:
        track_token = infos['TRACK_TOKEN']

    return track_token


def check_track_ids(infos: dict):
    if "FALLBACK" in infos:
        ids = infos['FALLBACK']['SNG_ID']
    else:
        ids = infos['SNG_ID']

    return ids


def __var_excape(string):
    string = (
        string
            .replace("\\", "")
            .replace("/", "")
            .replace(":", "")
            .replace("*", "")
            .replace("?", "")
            .replace("\"", "")
            .replace("<", "")
            .replace(">", "")
            .replace("|", "")
            .replace("&", "")
    )

    return string


def convert_to_date(date):
    if date == "0000-00-00":
        date = "0001-01-01"

    date = datetime.strptime(date, "%Y-%m-%d")
    return date


def what_kind(link):
    url = request(link).url
    return url


def __get_dir(song_metadata, output_dir, method_save):
    album = __var_excape(song_metadata['album'])
    artist = __var_excape(song_metadata['ar_album'])
    upc = song_metadata['upc']

    if method_save == 0:
        song_dir = f"{album} [{upc}]"

    elif method_save == 1:
        song_dir = f"{album} - {artist}"

    elif method_save == 2:
        song_dir = f"{album} - {artist} [{upc}]"

    song_dir = song_dir[:255]
    final_dir = join(output_dir, song_dir)
    final_dir += "/"
    return final_dir


def set_path(
        song_metadata, output_dir,
        song_quality, file_format, method_save
):
    album = __var_excape(song_metadata['album'])
    artist = __var_excape(song_metadata['artist'])
    music = __var_excape(song_metadata['music'])

    if method_save == 0:
        discnum = song_metadata['discnumber']
        tracknum = song_metadata['tracknumber']
        song_name = f"{album} CD {discnum} TRACK {tracknum}"

    elif method_save == 1:
        song_name = f"{music} - {artist}"

    elif method_save == 2:
        isrc = song_metadata['isrc']
        song_name = f"{music} - {artist} [{isrc}]"

    song_dir = __get_dir(song_metadata, output_dir, method_save)
    __check_dir(song_dir)

    l_encoded = len(
        song_name.encode()
    )

    if l_encoded > 242:
        n_tronc = l_encoded - 242
        n_tronc = len(song_name) - n_tronc
    else:
        n_tronc = 242

    song_path = f"{song_dir}{song_name[:n_tronc]}"
    song_path += f" ({song_quality}){file_format}"

    return song_path


def create_zip(
        tracks: [],
        output_dir=None,
        song_metadata=None,
        song_quality=None,
        method_save=0,
        zip_name=None
):
    if not zip_name:
        album = __var_excape(song_metadata['album'])
        song_dir = __get_dir(song_metadata, output_dir, method_save)

        if method_save == 0:
            zip_name = f"{song_dir}{album} ({song_quality})"

        elif method_save == 1:
            artist = __var_excape(song_metadata['ar_album'])
            zip_name = f"{song_dir}{album} - {artist} ({song_quality})"

        elif method_save == 2:
            artist = __var_excape(song_metadata['ar_album'])
            upc = song_metadata['upc']
            zip_name = f"{song_dir}{album} - {artist} {upc} ({song_quality})"

    zip_name += ".zip"
    z = ZipFile(zip_name, "w", ZIP_DEFLATED)

    for track in tracks:
        if not track.success:
            continue

        c_song_path = track.song_path
        song_path = basename(c_song_path)
        z.write(c_song_path, song_path)

    z.close()
    return zip_name


def trasform_sync_lyric(lyric):
    sync_array = []

    for a in lyric:
        if "milliseconds" in a:
            arr = (
                a['line'], int(a['milliseconds'])
            )

            sync_array.append(arr)

    return sync_array
