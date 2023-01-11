#!/usr/bin/python3

from time import sleep

from requests import get as req_get

from .settings import header
from .utils import artist_sort, convert_to_date
from .exceptions import (
	NoDataApi, QuotaExceeded, TrackNotFound
)


class API:
    def __init__(self):
        self.__api_link = "https://api.deezer.com/"
        self.__cover = "https://e-cdns-images.dzcdn.net/images/cover/%s/{}-000000-80-0-0.jpg"

    def __get_api(self, url, quota_exceeded=False):
        json = req_get(url, headers=header).json()

        if "error" in json:
            if json['error']['message'] == "no data":
                raise NoDataApi("No data avalaible :(")

            elif json['error']['message'] == "Quota limit exceeded":
                if not quota_exceeded:
                    sleep(0.8)
                    json = self.__get_api(url, True)
                else:
                    raise QuotaExceeded

        return json

    def get_chart(self, index=0):
        url = f"{self.__api_link}chart/{index}"
        infos = self.__get_api(url)
        return infos

    def get_track(self, ids):
        url = f"{self.__api_link}track/{ids}"
        infos = self.__get_api(url)
        return infos

    def get_album(self, ids):
        url = f"{self.__api_link}album/{ids}"
        infos = self.__get_api(url)
        return infos

    def get_playlist(self, ids):
        url = f"{self.__api_link}playlist/{ids}"
        infos = self.__get_api(url)
        return infos

    def get_artist(self, ids):
        url = f"{self.__api_link}artist/{ids}"
        infos = self.__get_api(url)
        return infos

    def get_artist_top_tracks(self, ids, limit=25):
        url = f"{self.__api_link}artist/{ids}/top?limit={limit}"
        infos = self.__get_api(url)
        return infos

    def get_artist_top_albums(self, ids, limit=25):
        url = f"{self.__api_link}artist/{ids}/albums?limit={limit}"
        infos = self.__get_api(url)
        return infos

    def get_artist_related(self, ids):
        url = f"{self.__api_link}artist/{ids}/related"
        infos = self.__get_api(url)
        return infos

    def get_artist_radio(self, ids):
        url = f"{self.__api_link}artist/{ids}/radio"
        infos = self.__get_api(url)
        return infos

    def get_artist_top_playlists(self, ids, limit=25):
        url = f"{self.__api_link}artist/{ids}/playlists?limit={limit}"
        infos = self.__get_api(url)
        return infos

    def search(self, query):
        url = f"{self.__api_link}search/?q={query}"
        infos = self.__get_api(url)

        if infos['total'] == 0:
            raise NoDataApi(query)

        return infos

    def search_track(self, query):
        url = f"{self.__api_link}search/track/?q={query}"
        infos = self.__get_api(url)

        if infos['total'] == 0:
            raise NoDataApi(query)

        return infos

    def search_album(self, query):
        url = f"{self.__api_link}search/album/?q={query}"
        infos = self.__get_api(url)

        if infos['total'] == 0:
            raise NoDataApi(query)

        return infos

    def search_playlist(self, query):
        url = f"{self.__api_link}search/playlist/?q={query}"
        infos = self.__get_api(url)

        if infos['total'] == 0:
            raise NoDataApi(query)

        return infos

    def search_artist(self, query):
        url = f"{self.__api_link}search/artist/?q={query}"
        infos = self.__get_api(url)

        if infos['total'] == 0:
            raise NoDataApi(query)

        return infos

    def not_found(self, song, title):
        try:
            data = self.search_track(song)['data']
        except NoDataApi:
            raise TrackNotFound(song)

        ids = None

        for track in data:
            if (
                    track['title'] == title
            ) or (
                    title in track['title_short']
            ):
                ids = track['id']
                break

        if not ids:
            raise TrackNotFound(song)

        return str(ids)

    def get_img_url(self, md5_image, size="1200x1200"):
        cover = self.__cover.format(size)
        image_url = cover % md5_image
        return image_url

    def choose_img(self, md5_image, size="1200x1200"):
        image_url = self.get_img_url(md5_image, size)
        image = req_get(image_url).content

        if len(image) == 13:
            image_url = self.get_img_url("", size)
            image = req_get(image_url).content

        return image

    def tracking(self, ids, album=False):
        datas = {}
        json_track = self.get_track(ids)

        if not album:
            album_ids = json_track['album']['id']
            json_album = self.get_album(album_ids)
            genres = []

            if "genres" in json_album:
                for genre in json_album['genres']['data']:
                    genres.append(genre['name'])

            datas['genre'] = " & ".join(genres)
            ar_album = []

            for contributor in json_album['contributors']:
                if contributor['role'] == "Main":
                    ar_album.append(contributor['name'])

            datas['ar_album'] = " & ".join(ar_album)
            datas['album'] = json_album['title']
            datas['label'] = json_album['label']
            datas['upc'] = json_album['upc']
            datas['nb_tracks'] = json_album['nb_tracks']

        datas['music'] = json_track['title']
        array = []

        for contributor in json_track['contributors']:
            if contributor['name'] != "":
                array.append(contributor['name'])

        array.append(
            json_track['artist']['name']
        )

        datas['artist'] = artist_sort(array)
        datas['tracknum'] = json_track['track_position']
        datas['discnum'] = json_track['disk_number']
        datas['year'] = convert_to_date(json_track['release_date'])
        datas['bpm'] = json_track['bpm']
        datas['duration'] = json_track['duration']
        datas['isrc'] = json_track['isrc']
        datas['gain'] = json_track['gain']
        return datas
