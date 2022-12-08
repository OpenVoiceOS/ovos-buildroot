from ovos_utils.ovos_service_api import OVOSApiService

from ovos_backend_client.backends.offline import BackendType, AbstractPartialBackend

OVOS_API_URL = "https://api.openvoiceos.com"
OVOS_STT_URL = "https://stt.openvoiceos.com/stt"


class OVOSAPIBackend(AbstractPartialBackend):

    def __init__(self, url=OVOS_API_URL, version="v1", identity_file=None, credentials=None):
        super().__init__(url, version, identity_file, BackendType.OVOS_API, credentials)
        self.client = OVOSApiService()

    @property
    def uuid(self):
        self.check_token()  # register device if needed
        return self.client.get_uuid()

    @property
    def access_token(self):
        self.check_token()
        return self.client.get_session_token()

    @property
    def headers(self):
        return {'session_challenge': self.access_token}

    def check_token(self):
        if not self.client.get_uuid():
            self.client.register_device()

    def refresh_token(self):
        self.check_token()

    # OWM Api
    def owm_get_weather(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location
        lat, lon = lat_lon or self._get_lat_lon()
        reqdata = {"lat": lat,
                   "lon": lon,
                   "units": units,
                   "lang": lang}
        url = f'{self.backend_url}/weather/onecall_weather_report/{self.uuid}'
        response = self.post(url, data=reqdata, headers={"backend": "OWM"})
        if response.status_code != 200:
            raise RuntimeError(f"OWM api failed, status_code {response.status_code}")
        response = response.json()
        if "error" in response:
            raise RuntimeError(response["error"])
        return response

    def owm_get_current(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location
        lat, lon = lat_lon or self._get_lat_lon()
        reqdata = {"lat": lat,
                   "lon": lon,
                   "units": units,
                   "lang": lang}
        url = f'{self.backend_url}/weather/generate_current_weather_report/{self.uuid}'
        response = self.post(url, data=reqdata, headers={"backend": "OWM"})
        if response.status_code != 200:
            raise RuntimeError(f"OWM api failed, status_code {response.status_code}")
        response = response.json()
        if "error" in response:
            raise RuntimeError(response["error"])
        return response

    def owm_get_hourly(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location

        lat, lon = lat_lon or self._get_lat_lon()
        reqdata = {"lat": lat,
                   "lon": lon,
                   "units": units,
                   "lang": lang}
        url = f'{self.backend_url}/weather/generate_hourly_weather_report/{self.uuid}'
        response = self.post(url, data=reqdata, headers={"backend": "OWM"})
        if response.status_code != 200:
            raise RuntimeError(f"OWM api failed, status_code {response.status_code}")
        response = response.json()
        if "error" in response:
            raise RuntimeError(response["error"])
        return response

    def owm_get_daily(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        raise KeyError("daily forecast API is non free")

    # Wolfram Alpha API
    def wolfram_spoken(self, query, units="metric", lat_lon=None, optional_params=None):
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'input': query,
                  "geolocation": "{},{}".format(*lat_lon),
                  'units': units,
                  **optional_params}
        url = f'{self.backend_url}/wolframalpha/spoken/{self.uuid}'
        data = self.post(url=url, params=params)
        return data.text

    def wolfram_simple(self, query, units="metric", lat_lon=None, optional_params=None):
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'input': query,
                  "geolocation": "{},{}".format(*lat_lon),
                  'units': units,
                  **optional_params}
        url = f'{self.backend_url}/wolframalpha/simple/{self.uuid}'
        data = self.get(url=url, params=params)
        return data.text

    def wolfram_full_results(self, query, units="metric", lat_lon=None, optional_params=None):
        """Wrapper for the WolframAlpha Full Results v2 API.
        https://products.wolframalpha.com/api/documentation/
        Pods of interest
        - Input interpretation - Wolfram's determination of what is being asked about.
        - Name - primary name of
        """
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'input': query,
                  "units": units,
                  "mode": "Default",
                  "format": "image,plaintext",
                  "geolocation": "{},{}".format(*lat_lon),
                  "output": "json",
                  **optional_params}
        url = f'{self.backend_url}/wolframalpha/full/{self.uuid}'
        data = self.get(url=url, params=params)
        return data.json()

    # Geolocation Api
    def geolocation_get(self, location):
        """Call the geolocation endpoint.

        Args:
            location (str): the location to lookup (e.g. Kansas City Missouri)

        Returns:
            str: JSON structure with lookup results
        """
        url = f"{self.backend_url}/geolocate/location/config"
        location = self.get(url, params={"address": location})
        location = location.json()
        if "timezone" not in location:
            location["timezone"] = self._get_timezone(
                lon=location["coordinate"]["longitude"],
                lat=location["coordinate"]["latitude"])
        return location

    # STT Api
    def stt_get(self, audio, language="en-us", limit=1):
        """ Web API wrapper for performing Speech to Text (STT)

        Args:
            audio (bytes): The recorded audio, as in a FLAC file
            language (str): A BCP-47 language code, e.g. "en-US"
            limit (int): Maximum alternate transcriptions

       """
        content_type = "audio/x-flac"

        data = self.post(OVOS_STT_URL, data=audio,
                         params={"lang": language, "limit": limit},
                         headers={"Content-Type": content_type})
        if data.status_code == 200:
            return [data.text]
        raise RuntimeError(f"STT api failed, status_code {data.status_code}")

    # Email API
    def email_send(self, title, body, sender):
        # get default recipient from config,
        # in ovos we dont have email tied to user accounts
        mail_config = self.credentials["email"]
        recipient = mail_config.get("recipient") or \
                    mail_config.get("smtp", {}).get("username")

        reqdata = {"recipient": recipient,
                   "subject": subject,
                   "body": body}
        url = f"{self.backend_url}/send/mail/{self.uuid}"
        requests.post(url, data=reqdata, headers=self.headers)



if __name__ == "__main__":
    b = OVOSAPIBackend()
    # a = b.geolocation_get("Fafe")
    a = b.wolfram_full_results("2+2")
    print(a)
    a = b.wolfram_spoken("what is the speed of light")
    print(a)
    a = b.wolfram_simple("what is the speed of light")
    print(a)
    exit()

    from speech_recognition import Recognizer, AudioFile

    with AudioFile("/home/user/PycharmProjects/selene_api/test/test.wav") as source:
        audio = Recognizer().record(source)

    flac_data = audio.get_flac_data()
    # a = b.stt_get(flac_data)

    a = b.owm_get_weather()
    # a = b.owm_get_daily()
    # a = b.owm_get_hourly()
    # a = b.owm_get_current()
    print(a)
