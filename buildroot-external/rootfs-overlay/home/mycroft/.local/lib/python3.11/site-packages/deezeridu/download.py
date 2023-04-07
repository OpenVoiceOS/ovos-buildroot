#!/usr/bin/python3

from copy import deepcopy
from os.path import isfile

from tqdm import tqdm

from .api import API
from .gateway import Gateway
from .settings import qualities
from .download_utils import decryptfile, gen_song_hash
from .taggers import write_tags, check_track
from .utils import (
	set_path, trasform_sync_lyric,
	create_zip, check_track_ids,
	check_track_md5, check_track_token
)
from .exceptions import (
	TrackNotFound, NoRightOnMedia, QualityNotFound
)
from .models import (
	Track, Album, Playlist,
	Preferences,
)


class DownloaderJob:
    def __init__(
            self,
            api: API,
            gw_api: Gateway
    ) -> None:

        self.api = api
        self.gw_api = gw_api

    def __get_url(
            self,
            c_track: Track,
            quality_download: str
    ) -> dict:

        c_md5, c_media_version = check_track_md5(c_track)
        c_ids = check_track_ids(c_track)
        n_quality = qualities[quality_download]['n_quality']

        c_song_hash = gen_song_hash(
            c_md5, n_quality,
            c_ids, c_media_version
        )

        c_media_url = self.gw_api.get_song_url(c_md5[0], c_song_hash)

        c_media_json = {
            "media": [
                {
                    "sources": [
                        {
                            "url": c_media_url
                        }
                    ]
                }
            ]
        }

        return c_media_json

    def check_sources(
            self,
            infos_dw: list,
            quality_download: str
    ) -> list:

        tracks_token = [
            check_track_token(c_track)
            for c_track in infos_dw
        ]

        try:
            medias = self.gw_api.get_medias_url(tracks_token, quality_download)

            for a in range(
                    len(medias)
            ):
                if "errors" in medias[a]:
                    c_media_json = self.__get_url(infos_dw[a],
                                                  quality_download)
                    medias[a] = c_media_json
                else:
                    if not medias[a]['media']:
                        c_media_json = self.__get_url(infos_dw[a],
                                                      quality_download)
                        medias[a] = c_media_json
        except NoRightOnMedia:
            medias = []

            for c_track in infos_dw:
                c_media_json = self.__get_url(c_track, quality_download)
                medias.append(c_media_json)

        return medias


class Downloader:
    def __init__(
            self,
            infos_dw: dict,
            preferences: Preferences,
            download_job: DownloaderJob,
    ) -> None:

        self.__download_job = download_job
        self.__api = download_job.api
        self.__gw_api = download_job.gw_api

        self.__infos_dw = infos_dw

        self.__ids = preferences.ids
        self.__link = preferences.link
        self.__output_dir = preferences.output_dir
        self.__method_save = preferences.method_save
        self.__song_metadata = preferences.song_metadata
        self.__not_interface = preferences.not_interface
        self.__quality_download = preferences.quality_download
        self.__recursive_quality = preferences.recursive_quality
        self.__recursive_download = preferences.recursive_download

        self.__c_quality = qualities[self.__quality_download]
        self.__set_quality()
        self.__set_song_path()

    def __set_quality(self) -> None:
        self.__file_format = self.__c_quality['f_format']
        self.__song_quality = self.__c_quality['s_quality']

    def __set_song_path(self) -> None:
        self.__song_path = set_path(
            self.__song_metadata,
            self.__output_dir,
            self.__song_quality,
            self.__file_format,
            self.__method_save
        )

    def __write_track(self) -> None:
        self.__set_song_path()

        self.__c_track = Track(
            self.__song_metadata, self.__song_path,
            self.__file_format, self.__song_quality,
            self.__link, self.__ids
        )

    def easy_dw(self) -> Track:
        pic = self.__infos_dw['ALB_PICTURE']
        image = self.__api.choose_img(pic)
        self.__song_metadata['image'] = image
        song = f"{self.__song_metadata['music']} - {self.__song_metadata['artist']}"

        if not self.__not_interface:
            print(f"Downloading: {song}")

        try:
            self.download_try()
        except TrackNotFound:
            try:
                ids = self.__api.not_found(song, self.__song_metadata['music'])
                self.__infos_dw = self.__gw_api.get_song_data(ids)

                media = self.__download_job.check_sources(
                    [self.__infos_dw], self.__quality_download
                )

                self.__infos_dw['media_url'] = media[0]
                self.download_try()
            except TrackNotFound:
                self.__c_track = Track(
                    self.__song_metadata,
                    None, None,
                    None, None, None,
                )

                self.__c_track.success = False

        self.__c_track.md5_image = pic

        return self.__c_track

    def download_try(self) -> Track:
        self.__c_track = Track(
            self.__song_metadata, self.__song_path,
            self.__file_format, self.__song_quality,
            self.__link, self.__ids
        )

        if isfile(self.__song_path):
            if check_track(self.__c_track):
                return self.__c_track

        media_list = self.__infos_dw['media_url']['media']
        song_link = media_list[0]['sources'][0]['url']

        try:
            crypted_audio = self.__gw_api.song_exist(song_link)
        except TrackNotFound:
            song = self.__song_metadata['music']
            artist = self.__song_metadata['artist']
            msg = f"\n⚠ The {song} - {artist} can't be downloaded in {self.__quality_download} quality :( ⚠\n"

            if not self.__recursive_quality:
                raise QualityNotFound(msg=msg)

            print(msg)

            for c_quality in qualities:
                if self.__quality_download == c_quality:
                    continue

                print(
                    f"🛈 Trying to download {song} - {artist} in {c_quality}")

                media = self.__download_job.check_sources(
                    [self.__infos_dw], c_quality
                )

                self.__infos_dw['media_url'] = media[0]
                c_media = self.__infos_dw['media_url']
                media_list = c_media['media']
                song_link = media_list[0]['sources'][0]['url']

                try:
                    crypted_audio = self.__gw_api.song_exist(song_link)
                    self.__c_quality = qualities[c_quality]
                    self.__set_quality()
                    break
                except TrackNotFound:
                    if c_quality == "MP3_128":
                        raise TrackNotFound("Error with this song",
                                            self.__link)

        self.__write_track()
        c_crypted_audio = crypted_audio.iter_content(2048)
        c_ids = check_track_ids(self.__infos_dw)
        self.__c_track.set_fallback_ids(c_ids)

        decryptfile(
            c_crypted_audio, c_ids, self.__song_path
        )

        self.__add_more_tags()
        write_tags(self.__c_track)

        return self.__c_track

    def __add_more_tags(self) -> None:
        contributors = self.__infos_dw['SNG_CONTRIBUTORS']

        if "author" in contributors:
            self.__song_metadata['author'] = " & ".join(
                contributors['author']
            )
        else:
            self.__song_metadata['author'] = ""

        if "composer" in contributors:
            self.__song_metadata['composer'] = " & ".join(
                contributors['composer']
            )
        else:
            self.__song_metadata['composer'] = ""

        if "lyricist" in contributors:
            self.__song_metadata['lyricist'] = " & ".join(
                contributors['lyricist']
            )
        else:
            self.__song_metadata['lyricist'] = ""

        if "composerlyricist" in contributors:
            self.__song_metadata['composer'] = " & ".join(
                contributors['composerlyricist']
            )
        else:
            self.__song_metadata['composerlyricist'] = ""

        if "version" in self.__infos_dw:
            self.__song_metadata['version'] = self.__infos_dw['VERSION']
        else:
            self.__song_metadata['version'] = ""

        self.__song_metadata['lyric'] = ""
        self.__song_metadata['copyright'] = ""
        self.__song_metadata['lyricist'] = ""
        self.__song_metadata['lyric_sync'] = []

        if self.__infos_dw['LYRICS_ID'] != 0:
            need = self.__gw_api.get_lyric(self.__ids)

            if "LYRICS_SYNC_JSON" in need:
                self.__song_metadata['lyric_sync'] = trasform_sync_lyric(
                    need['LYRICS_SYNC_JSON']
                )

            self.__song_metadata['lyric'] = need['LYRICS_TEXT']
            self.__song_metadata['copyright'] = need['LYRICS_COPYRIGHTS']
            self.__song_metadata['lyricist'] = need['LYRICS_WRITERS']


class TrackDownloader:
    def __init__(
            self,
            preferences: Preferences,
            download_job: DownloaderJob
    ) -> None:
        self.__download_job = download_job
        self.__gw_api = download_job.gw_api

        self.__preferences = preferences
        self.__ids = self.__preferences.ids
        self.__song_metadata = self.__preferences.song_metadata
        self.__quality_download = self.__preferences.quality_download

    def dw(self) -> Track:
        infos_dw = self.__gw_api.get_song_data(self.__ids)

        media = self.__download_job.check_sources(
            [infos_dw], self.__quality_download
        )

        infos_dw['media_url'] = media[0]

        track = Downloader(
            infos_dw, self.__preferences, self.__download_job,
        ).easy_dw()

        if not track.success:
            song = f"{self.__song_metadata['music']} - {self.__song_metadata['artist']}"
            error_msg = f"Cannot download {song}"

            raise TrackNotFound(message=error_msg)

        return track


class AlbumDownloader:
    def __init__(
            self,
            preferences: Preferences,
            download_job: DownloaderJob
    ) -> None:

        self.__api = download_job.api
        self.__download_job = download_job
        self.__gw_api = download_job.gw_api

        self.__preferences = preferences
        self.__ids = self.__preferences.ids
        self.__make_zip = self.__preferences.make_zip
        self.__output_dir = self.__preferences.output_dir
        self.__method_save = self.__preferences.method_save
        self.__song_metadata = self.__preferences.song_metadata
        self.__not_interface = self.__preferences.not_interface
        self.__quality_download = self.__preferences.quality_download

        self.__song_metadata_items = self.__song_metadata.items()

    def dw(self) -> Album:
        infos_dw = self.__gw_api.get_album_data(self.__ids)['data']
        md5_image = infos_dw[0]['ALB_PICTURE']
        image = self.__api.choose_img(md5_image)
        self.__song_metadata['image'] = image

        album = Album(self.__ids)
        album.image = image
        album.md5_image = md5_image
        album.nb_tracks = self.__song_metadata['nb_tracks']
        album.album_name = self.__song_metadata['album']
        album.upc = self.__song_metadata['upc']
        tracks = album.tracks

        medias = self.__download_job.check_sources(
            infos_dw, self.__quality_download
        )

        c_song_metadata = {}

        for key, item in self.__song_metadata_items:
            if type(item) is not list:
                c_song_metadata[key] = self.__song_metadata[key]

        t = tqdm(
            range(
                len(infos_dw)
            ),
            desc=c_song_metadata['album'],
            disable=self.__not_interface
        )

        for a in t:
            for key, item in self.__song_metadata_items:
                if type(item) is list:
                    c_song_metadata[key] = self.__song_metadata[key][a]

            c_infos_dw = infos_dw[a]
            c_infos_dw['media_url'] = medias[a]
            song = f"{c_song_metadata['music']} - {c_song_metadata['artist']}"
            t.set_description_str(song)
            c_preferences = deepcopy(self.__preferences)
            c_preferences.song_metadata = c_song_metadata
            c_preferences.ids = c_infos_dw['SNG_ID']

            try:
                track = Downloader(
                    c_infos_dw, c_preferences, self.__download_job
                ).download_try()

                tracks.append(track)
            except TrackNotFound:
                try:
                    ids = self.__api.not_found(song, c_song_metadata['music'])
                    c_song_data = self.__gw_api.get_song_data(ids)

                    c_media = self.__download_job.check_sources(
                        [c_song_data], self.__quality_download
                    )

                    c_infos_dw['media_url'] = c_media[0]

                    track = Downloader(
                        c_infos_dw, c_preferences, self.__download_job
                    ).download_try()

                    tracks.append(track)
                except TrackNotFound:
                    track = Track(
                        c_song_metadata,
                        None, None,
                        None, None, None,
                    )

                    track.success = False
                    tracks.append(track)
                    print(f"Track not found: {song} :(")
                    continue

        if self.__make_zip:
            song_quality = tracks[0].quality

            zip_name = create_zip(
                tracks,
                output_dir=self.__output_dir,
                song_metadata=self.__song_metadata,
                song_quality=song_quality,
                method_save=self.__method_save
            )

            album.zip_path = zip_name

        return album


class PlaylistDownloader:
    def __init__(
            self,
            preferences: Preferences,
            download_job: DownloaderJob
    ) -> None:

        self.__download_job = download_job
        self.__gw_api = download_job.gw_api

        self.__preferences = preferences
        self.__ids = self.__preferences.ids
        self.__json_data = preferences.json_data
        self.__make_zip = self.__preferences.make_zip
        self.__output_dir = self.__preferences.output_dir
        self.__song_metadata = self.__preferences.song_metadata
        self.__quality_download = self.__preferences.quality_download

    def dw(self) -> Playlist:
        infos_dw = self.__gw_api.get_playlist_data(self.__ids)['data']

        playlist = Playlist()
        tracks = playlist.tracks

        medias = self.__download_job.check_sources(
            infos_dw, self.__quality_download
        )

        for c_infos_dw, c_media, c_song_metadata in zip(
                infos_dw, medias, self.__song_metadata
        ):
            c_infos_dw['media_url'] = c_media
            c_preferences = deepcopy(self.__preferences)
            c_preferences.ids = c_infos_dw['SNG_ID']
            c_preferences.song_metadata = c_song_metadata
            c_song_metadata = c_preferences.song_metadata

            if type(c_song_metadata) is str:
                print(f"Track not found {c_song_metadata} :(")
                continue

            track = Downloader(
                c_infos_dw, c_preferences, self.__download_job
            ).easy_dw()

            if not track.success:
                song = f"{c_song_metadata['music']} - {c_song_metadata['artist']}"
                print(f"Cannot download {song}")

            tracks.append(track)

        if self.__make_zip:
            playlist_title = self.__json_data['title']
            zip_name = f"{self.__output_dir}/{playlist_title} [playlist {self.__ids}]"
            create_zip(tracks, zip_name=zip_name)
            playlist.zip_path = zip_name

        return playlist
