#!/usr/bin/python3

from requests import Session
from requests import (
	get as req_get,
	post as req_post
)

from .settings import qualities
from .download_utils import md5hex
from .exceptions import (
	BadCredentials, TrackNotFound, NoRightOnMedia
)

client_id = "172365"
client_secret = "fb0bec7ccc063dab0417eb7b0d847f34"
try_link = "https://api.deezer.com/platform/generic/track/3135556"


class Gateway:
    def __init__(
            self,
            arl=None,
            email=None,
            password=None
    ):
        self.__req = Session()
        self.__arl = arl
        self.__email = email
        self.__password = password
        self.__token = "null"
        self.__get_lyric = "song.getLyrics"
        self.__get_song_data = "song.getData"
        self.__get_user_getArl = "user.getArl"
        self.__get_page_track = "deezer.pageTrack"
        self.__get_user_data = "deezer.getUserData"
        self.__get_album_data = "song.getListByAlbum"
        self.__get_playlist_data = "playlist.getSongs"
        self.__get_media_url = "https://media.deezer.com/v1/get_url"
        self.__get_auth_token_url = "https://api.deezer.com/auth/token"
        self.__private_api_link = "https://www.deezer.com/ajax/gw-light.php"
        self.__song_server = "https://e-cdns-proxy-{}.dzcdn.net/mobile/1/{}"
        self.__refresh_token()

    def __login(self):
        if (
                (not self.__arl) and
                (not self.__email) and
                (not self.__password)
        ):
            msg = f"NO LOGIN STUFF INSERTED :)))"

            raise BadCredentials(msg=msg)

        if self.__arl:
            self.__req.cookies['arl'] = self.__arl
        else:
            self.__get_arl()

    def __get_arl(self):
        access_token = self.__get_access_token()

        c_headers = {
            "Authorization": f"Bearer {access_token}"
        }

        self.__req.get(try_link, headers=c_headers).json()
        arl = self.__get_api(self.__get_user_getArl)
        self.__req.cookies.get("sid")
        self.__arl = arl

    def __get_access_token(self):
        password = md5hex(self.__password)

        request_hash = md5hex(
            "".join(
                [
                    client_id, self.__email, password, client_secret
                ]
            )
        )

        params = {
            "app_id": client_id,
            "login": self.__email,
            "password": password,
            "hash": request_hash
        }

        results = req_get(self.__get_auth_token_url, params=params).json()

        if "error" in results:
            raise BadCredentials(
                email=self.__email,
                password=self.__password
            )

        access_token = results['access_token']

        return access_token

    def __cool_api(self):
        guest_sid = self.__req.cookies.get("sid")
        url = "https://api.deezer.com/1.0/gateway.php"

        params = {
            'api_key': "4VCYIJUCDLOUELGD1V8WBVYBNVDYOXEWSLLZDONGBBDFVXTZJRXPR29JRLQFO6ZE",
            'sid': guest_sid,
            'input': '3',
            'output': '3',
            'method': 'song_getData'
        }

        json = {'sng_id': 302127}

        json = req_post(url, params=params, json=json).json()
        print(json)

    def __get_api(
            self, method,
            json_data=None
    ):
        params = {
            "api_version": "1.0",
            "api_token": self.__token,
            "input": "3",
            "method": method
        }

        results = self.__req.post(
            self.__private_api_link,
            params=params,
            json=json_data
        ).json()['results']

        if not results:
            self.__refresh_token()
            self.__get_api(method, json_data)

        return results

    def get_user(self):
        data = self.__get_api(self.__get_user_data)
        return data

    def __refresh_token(self):
        self.__req.cookies.clear_session_cookies()

        if not self.amIlog():
            self.__login()
            self.am_I_log()

        data = self.get_user()
        self.__token = data['checkForm']
        self.__license_token = self.__get_license_token()

    def __get_license_token(self):
        data = self.get_user()
        license_token = data['USER']['OPTIONS']['license_token']

        return license_token

    def amIlog(self):
        data = self.get_user()
        user_id = data['USER']['USER_ID']
        is_logged = False

        if user_id != 0:
            is_logged = True

        return is_logged

    def am_I_log(self):
        if not self.amIlog():
            raise BadCredentials(arl=self.__arl)

    def get_song_data(self, ids):
        json_data = {
            "sng_id": ids
        }

        infos = self.__get_api(self.__get_song_data, json_data)

        return infos

    def get_album_data(self, ids):
        json_data = {
            "alb_id": ids,
            "nb": -1
        }

        infos = self.__get_api(self.__get_album_data, json_data)

        return infos

    def get_lyric(self, ids):
        json_data = {
            "sng_id": ids
        }

        infos = self.__get_api(self.__get_lyric, json_data)

        return infos

    def get_playlist_data(self, ids):
        json_data = {
            "playlist_id": ids,
            "nb": -1
        }

        infos = self.__get_api(self.__get_playlist_data, json_data)

        return infos

    def get_page_track(self, ids):
        json_data = {
            "sng_id": ids
        }

        infos = self.__get_api(self.__get_page_track, json_data)

        return infos

    def get_song_url(self, n, song_hash):
        song_url = self.__song_server.format(n, song_hash)

        return song_url

    def song_exist(self, song_url):
        crypted_audio = req_get(song_url)

        if len(crypted_audio.content) == 0:
            raise TrackNotFound

        return crypted_audio

    def get_medias_url(self, tracks_token, quality):
        others_qualities = []

        for c_quality in qualities:
            if c_quality == quality:
                continue

            c_quality_set = {
                "cipher": "BF_CBC_STRIPE",
                "format": c_quality
            }

            others_qualities.append(c_quality_set)

        json_data = {
            "license_token": self.__license_token,
            "media": [
                {
                    "type": "FULL",
                    "formats": [
                        {
                            "cipher": "BF_CBC_STRIPE",
                            "format": quality
                        }
                    ]  # + others_qualities
                }
            ],
            "track_tokens": tracks_token
        }

        infos = req_post(
            self.__get_media_url,
            json=json_data
        ).json()

        if "errors" in infos:
            msg = infos['errors'][0]['message']

            raise NoRightOnMedia(msg)

        medias = infos['data']

        return medias
