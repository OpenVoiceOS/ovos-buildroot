from ovos_utils import timed_lru_cache
from ovos_utils.log import LOG

from ovos_backend_client.backends import OfflineBackend, OVOSAPIBackend, \
    SeleneBackend, PersonalBackend, BackendType, get_backend_config, API_REGISTRY


class BaseApi:
    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None, credentials=None):
        url, version, identity_file, backend_type = get_backend_config(url, version,
                                                                       identity_file, backend_type)
        self.url = url
        self.credentials = credentials or {}
        if backend_type == BackendType.SELENE:
            self.backend = SeleneBackend(url, version, identity_file)
        elif backend_type == BackendType.PERSONAL:
            self.backend = PersonalBackend(url, version, identity_file)
        elif backend_type == BackendType.OVOS_API:
            self.backend = OVOSAPIBackend(url, version, identity_file)
        else:  # if backend_type == BackendType.OFFLINE:
            self.backend = OfflineBackend(url, version, identity_file)
        self.validate_backend_type()

    def validate_backend_type(self):
        pass

    @property
    def backend_type(self):
        return self.backend.backend_type

    @property
    def backend_url(self):
        if not self.backend.url.startswith("http"):
            self.backend.url = f"http://{self.backend.url}"
        return self.backend.url

    @property
    def backend_version(self):
        return self.backend.backend_version

    @property
    def identity(self):
        return self.backend.identity

    @property
    def uuid(self):
        return self.backend.uuid

    @property
    def access_token(self):
        return self.backend.access_token

    @property
    def headers(self):
        return self.backend.headers

    def check_token(self):
        self.backend.check_token()

    def refresh_token(self):
        self.backend.refresh_token()

    def get(self, url=None, *args, **kwargs):
        return self.backend.get(url, *args, **kwargs)

    def post(self, url=None, *args, **kwargs):
        return self.backend.post(url, *args, **kwargs)

    def put(self, url=None, *args, **kwargs):
        return self.backend.put(url, *args, **kwargs)

    def patch(self, url=None, *args, **kwargs):
        return self.backend.patch(url, *args, **kwargs)


class AdminApi(BaseApi):
    def __init__(self, admin_key, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type, credentials={"admin": admin_key})
        self.url = f"{self.backend_url}/{self.backend_version}/admin"

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["admin"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")

    def pair(self, uuid=None):
        return self.backend.admin_pair(uuid)

    def set_device_location(self, uuid, loc):
        """
        loc = {
            "city": {
                "code": "Lawrence",
                "name": "Lawrence",
                "state": {
                    "code": "KS",
                    "name": "Kansas",
                    "country": {
                        "code": "US",
                        "name": "United States"
                    }
                }
            },
            "coordinate": {
                "latitude": 38.971669,
                "longitude": -95.23525
            },
            "timezone": {
                "code": "America/Chicago",
                "name": "Central Standard Time",
                "dstOffset": 3600000,
                "offset": -21600000
            }
        }
        """
        return self.backend.admin_set_device_location(uuid, loc)

    def set_device_prefs(self, uuid, prefs):
        """
        prefs = {"time_format": "full",
                "date_format": "DMY",
                "system_unit": "metric",
                "lang": "en-us",
                "wake_word": "hey_mycroft",
                "ww_config": {"phonemes": "HH EY . M AY K R AO F T",
                             "module": "ovos-ww-plugin-pocketsphinx",
                             "threshold": 1e-90},
                "tts_module": "ovos-tts-plugin-mimic",
                "tts_config": {"voice": "ap"}}
        """
        self.backend.admin_set_device_prefs(uuid, prefs)

    def set_device_info(self, uuid, info):
        """
        info = {"opt_in": True,
                "name": "my_device",
                "device_location": "kitchen",
                "email": "notifications@me.com",
                "isolated_skills": False,
                "lang": "en-us"}
        """
        self.backend.admin_set_device_info(uuid, info)


class DeviceApi(BaseApi):
    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)
        self.url = f"{self.backend_url}/{self.backend_version}/device"

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["device"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")

    def get(self, url=None, *args, **kwargs):
        """ Retrieve all device information from the web backend """
        return self.backend.device_get()

    def get_skill_settings_v1(self):
        """ old style deprecated bidirectional skill settings api, still available! """
        return self.backend.device_get_skill_settings_v1()

    def put_skill_settings_v1(self, data):
        """ old style deprecated bidirectional skill settings api, still available! """
        return self.backend.device_put_skill_settings_v1(data)

    def get_settings(self):
        """ Retrieve device settings information from the web backend

        Returns:
            str: JSON string with user configuration information.
        """
        return self.backend.device_get_settings()

    def get_code(self, state=None):
        return self.backend.device_get_code(state)

    def activate(self, state, token,
                 core_version="unknown",
                 platform="unknown",
                 platform_build="unknown",
                 enclosure_version="unknown"):
        return self.backend.device_activate(state, token, core_version,
                                            platform, platform_build, enclosure_version)

    def update_version(self,
                       core_version="unknown",
                       platform="unknown",
                       platform_build="unknown",
                       enclosure_version="unknown"):
        return self.backend.device_update_version(core_version, platform, platform_build, enclosure_version)

    def report_metric(self, name, data):
        return self.backend.device_report_metric(name, data)

    def get_location(self):
        """ Retrieve device location information from the web backend

        Returns:
            str: JSON string with user location.
        """
        return self.backend.device_get_location()

    def get_subscription(self):
        """
            Get information about type of subscription this unit is connected
            to.

            Returns: dictionary with subscription information
        """
        return self.backend.device_get_subscription()

    @property
    def is_subscriber(self):
        """
            status of subscription. True if device is connected to a paying
            subscriber.
        """
        return self.backend.is_subscriber

    def get_subscriber_voice_url(self, voice=None, arch=None):
        return self.backend.device_get_subscriber_voice_url(voice, arch)

    def get_oauth_token(self, dev_cred):
        """
            Get Oauth token for dev_credential dev_cred.

            Argument:
                dev_cred:   development credentials identifier

            Returns:
                json string containing token and additional information
        """
        return self.backend.device_get_oauth_token(dev_cred)

    # cached for 30 seconds because often 1 call per skill is done in quick succession
    @timed_lru_cache(seconds=30)
    def get_skill_settings(self):
        """Get the remote skill settings for all skills on this device."""
        return self.backend.device_get_skill_settings()

    def send_email(self, title, body, sender):
        return self.backend.device_send_email(title, body, sender)

    def upload_skill_metadata(self, settings_meta):
        """Upload skill metadata.

        Args:
            settings_meta (dict): skill info and settings in JSON format
        """
        return self.backend.device_upload_skill_metadata(settings_meta)

    def upload_skills_data(self, data):
        """ Upload skills.json file. This file contains a manifest of installed
        and failed installations for use with the Marketplace.

        Args:
             data: dictionary with skills data from msm
        """
        if not isinstance(data, dict):
            raise ValueError('data must be of type dict')

        _data = dict(data)  # Make sure the input data isn't modified
        # Strip the skills.json down to the bare essentials
        to_send = {'skills': []}
        if 'blacklist' in _data:
            to_send['blacklist'] = _data['blacklist']
        else:
            LOG.warning('skills manifest lacks blacklist entry')
            to_send['blacklist'] = []

        # Make sure skills doesn't contain duplicates (keep only last)
        if 'skills' in _data:
            skills = {s['name']: s for s in _data['skills']}
            to_send['skills'] = [skills[key] for key in skills]
        else:
            LOG.warning('skills manifest lacks skills entry')
            to_send['skills'] = []

        for s in to_send['skills']:
            # Remove optional fields backend objects to
            if 'update' in s:
                s.pop('update')

            # Finalize skill_gid with uuid if needed
            s['skill_gid'] = s.get('skill_gid', '').replace('@|', f'@{self.uuid}|')

        return self.backend.device_upload_skills_data(to_send)

    def upload_wake_word_v1(self, audio, params):
        """ upload precise wake word V1 endpoint - DEPRECATED"""
        return self.backend.device_upload_wake_word_v1(audio, params)

    def upload_wake_word(self, audio, params):
        """ upload precise wake word V2 endpoint """
        return self.backend.device_upload_wake_word(audio, params)


class STTApi(BaseApi):
    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)
        self.url = f"{self.backend_url}/{self.backend_version}/stt"

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["stt"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")

    @property
    def headers(self):
        h = self.backend.headers
        h["Content-Type"] = "audio/x-flac"
        return h

    def stt(self, audio, language="en-us", limit=1):
        """ Web API wrapper for performing Speech to Text (STT)

        Args:
            audio (bytes): The recorded audio, as in a FLAC file
            language (str): A BCP-47 language code, e.g. "en-US"
            limit (int): Maximum minutes to transcribe(?)

        Returns:
            dict: JSON structure with transcription results
        """
        return self.backend.stt_get(audio, language, limit)


class GeolocationApi(BaseApi):
    """Web API wrapper for performing geolocation lookups."""

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["geolocate"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")
        if self.backend_type == BackendType.OVOS_API:
            self.url = f"{self.backend_url}/geolocate"
        elif self.backend_type == BackendType.OFFLINE:
            self.url = "https://nominatim.openstreetmap.org"
        else:
            self.url = f"{self.backend_url}/{self.backend_version}/geolocation"

    def get_geolocation(self, location):
        """Call the geolocation endpoint.

        Args:
            location (str): the location to lookup (e.g. Kansas City Missouri)

        Returns:
            str: JSON structure with lookup results
        """
        return self.backend.geolocation_get(location)


class WolframAlphaApi(BaseApi):

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None, key=None):
        super().__init__(url, version, identity_file, backend_type, credentials={"wolfram": key})

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["wolfram"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")
        if self.backend_type == BackendType.OFFLINE and not self.credentials["wolfram"]:
            raise ValueError("WolframAlpha api key not set!")

        if self.backend_type == BackendType.OVOS_API:
            self.url = f"{self.backend_url}/wolframalpha"
        elif self.backend_type == BackendType.OFFLINE:
            self.url = "https://api.wolframalpha.com"
        else:
            self.url = f"{self.backend_url}/{self.backend_version}/wolframAlpha"

    # cached to save api calls, wolfram answer wont change often
    @timed_lru_cache(seconds=60 * 30)
    def spoken(self, query, units="metric", lat_lon=None, optional_params=None):
        return self.backend.wolfram_spoken(query, units, lat_lon, optional_params)

    @timed_lru_cache(seconds=60 * 30)
    def simple(self, query, units="metric", lat_lon=None, optional_params=None):
        return self.backend.wolfram_simple(query, units, lat_lon, optional_params)

    @timed_lru_cache(seconds=60 * 30)
    def full_results(self, query, units="metric", lat_lon=None, optional_params=None):
        """Wrapper for the WolframAlpha Full Results v2 API.
            https://products.wolframalpha.com/api/documentation/
            Pods of interest
            - Input interpretation - Wolfram's determination of what is being asked about.
            - Name - primary name of
            """
        return self.backend.wolfram_full_results(query, units, lat_lon, optional_params)


class OpenWeatherMapApi(BaseApi):
    """Use Open Weather Map's One Call API to retrieve weather information"""

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None, key=None):
        super().__init__(url, version, identity_file, backend_type, credentials={"owm": key})

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["owm"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")
        if self.backend_type == BackendType.OFFLINE and not self.backend.credentials["owm"]:
            raise ValueError("OWM api key not set!")
        if self.backend_type == BackendType.OVOS_API:
            self.url = f"{self.backend_url}/weather"
        elif self.backend_type == BackendType.OFFLINE:
            self.url = "https://api.openweathermap.org/data/2.5"
        else:
            self.url = f"{self.backend_url}/{self.backend_version}/owm"

    def owm_language(self, lang: str):
        """
        OWM supports 31 languages, see https://openweathermap.org/current#multi

        Convert Mycroft's language code to OpenWeatherMap's, if missing use english.

        Args:
            lang: The Mycroft language code.
        """
        return self.backend.owm_language(lang)

    # cached to save api calls, owm only updates data every 15mins or so
    @timed_lru_cache(seconds=60 * 10)
    def get_weather(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        return self.backend.owm_get_weather(lat_lon, lang, units)

    @timed_lru_cache(seconds=60 * 10)
    def get_current(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        return self.backend.owm_get_current(lat_lon, lang, units)

    @timed_lru_cache(seconds=60 * 10)
    def get_hourly(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        return self.backend.owm_get_hourly(lat_lon, lang, units)

    @timed_lru_cache(seconds=60 * 10)
    def get_daily(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        return self.backend.owm_get_daily(lat_lon, lang, units)


class EmailApi(BaseApi):
    """Web API wrapper for sending email"""

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["email"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")
        if self.backend_type == BackendType.OFFLINE:
            self.url = self.credentials["smtp"]["host"]
        else:
            self.url = self.backend_url

    def send_email(self, title, body, sender):
        return self.backend.email_send(title, body, sender)


class DatasetApi(BaseApi):
    """Web API wrapper for dataset collection"""

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["dataset"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")

    def upload_wake_word(self, audio, params, upload_url=None):
        return self.backend.dataset_upload_wake_word(audio, params, upload_url)


class MetricsApi(BaseApi):
    """Web API wrapper for netrics collection"""

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["metrics"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")

    def report_metric(self, name, data):
        return self.backend.metrics_upload(name, data)


class OAuthApi(BaseApi):
    """Web API wrapper for oauth api"""

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=None):
        super().__init__(url, version, identity_file, backend_type)

    def validate_backend_type(self):
        if not API_REGISTRY[self.backend_type]["oauth"]:
            raise ValueError(f"{self.__class__.__name__} not available for {self.backend_type}")

    def get_oauth_token(self, dev_cred):
        """
            Get Oauth token for dev_credential dev_cred.

            Argument:
                dev_cred:   development credentials identifier

            Returns:
                json string containing token and additional information
        """
        return self.backend.oauth_get_token(dev_cred)


if __name__ == "__main__":
    # d = DeviceApi(FAKE_BACKEND_URL)

    # TODO turn these into unittests
    # ident = load_identity()
    # paired = is_paired()
    geo = GeolocationApi(backend_type=BackendType.OFFLINE)
    data = geo.get_geolocation("Missouri Kansas")
    print(data)
    exit(6)
    wolf = WolframAlphaApi(backend_type=BackendType.OFFLINE)
    # data = wolf.spoken("what is the speed of light")
    # print(data)
    # data = wolf.full_results("2+2")
    # print(data)

    owm = OpenWeatherMapApi(backend_type=BackendType.OFFLINE)
    data = owm.get_current()
    print(data)
    data = owm.get_weather()
    print(data)
