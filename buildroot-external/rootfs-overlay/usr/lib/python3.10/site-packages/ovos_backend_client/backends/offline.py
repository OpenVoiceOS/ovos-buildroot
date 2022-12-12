import json
import time
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
from uuid import uuid4

from json_database import JsonStorageXDG
from ovos_config.config import Configuration
from ovos_config.config import update_mycroft_config
from ovos_plugin_manager.stt import OVOSSTTFactory, get_stt_config
from ovos_utils.smtp_utils import send_smtp

from ovos_backend_client.identity import IdentityManager
from ovos_backend_client.backends.base import AbstractBackend, BackendType
from ovos_backend_client.database import BackendDatabase


class OfflineBackend(AbstractBackend):

    def __init__(self, url="127.0.0.1", version="v1", identity_file=None, credentials=None):
        super().__init__(url, version, identity_file, BackendType.OFFLINE, credentials)
        self.stt = None

    # OWM API
    def owm_get_weather(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location

        lat, lon = lat_lon or self._get_lat_lon()
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.credentials["owm"]
        }
        url = "https://api.openweathermap.org/data/2.5/onecall"
        response = self.get(url, params=params)
        return response.json()

    def owm_get_current(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location

        lat, lon = lat_lon or self._get_lat_lon()
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.credentials["owm"]
        }
        url = "https://api.openweathermap.org/data/2.5/weather"
        response = self.get(url, params=params)
        return response.json()

    def owm_get_hourly(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location

        lat, lon = lat_lon or self._get_lat_lon()
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.credentials["owm"]
        }
        url = "https://api.openweathermap.org/data/2.5/forecast"
        response = self.get(url, params=params)
        return response.json()

    def owm_get_daily(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location

        lat, lon = lat_lon or self._get_lat_lon()
        params = {
            "lang": lang,
            "units": units,
            "lat": lat, "lon": lon,
            "appid": self.credentials["owm"]
        }
        url = "https://api.openweathermap.org/data/2.5/forecast/daily"
        response = self.get(url, params=params)
        return response.json()

    # Wolfram Alpha Api
    def wolfram_spoken(self, query, units="metric", lat_lon=None, optional_params=None):
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'i': query,
                  "geolocation": "{},{}".format(*lat_lon),
                  'units': units,
                  **optional_params}
        url = 'https://api.wolframalpha.com/v1/spoken'
        params["appid"] = self.credentials["wolfram"]
        return self.get(url, params=params).text

    def wolfram_simple(self, query, units="metric", lat_lon=None, optional_params=None):
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'i': query,
                  "geolocation": "{},{}".format(*lat_lon),
                  'units': units,
                  **optional_params}
        url = 'https://api.wolframalpha.com/v1/simple'
        params["appid"] = self.credentials["wolfram"]
        return self.get(url, params=params).text

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
        url = 'https://api.wolframalpha.com/v2/query'
        params["appid"] = self.credentials["wolfram"]
        data = self.get(url, params=params)
        return data.json()

    # Geolocation Api
    def geolocation_get(self, location):
        """Call the geolocation endpoint.

        Args:
            location (str): the location to lookup (e.g. Kansas City Missouri)

        Returns:
            str: JSON structure with lookup results
        """
        url = "https://nominatim.openstreetmap.org/search"
        data = self.get(url, params={"q": location, "format": "json", "limit": 1}).json()[0]
        url = "https://nominatim.openstreetmap.org/details.php?osmtype=W&osmid=38210407&format=json"
        details = self.get(url, params={"osmid": data['osm_id'], "osmtype": data['osm_type'][0].upper(),
                                        "format": "json"}).json()

        location = {
            "city": {
                "code": details["addresstags"].get("postcode") or details["calculated_postcode"] or "",
                "name": details["localname"],
                "state": {
                    "code": details["addresstags"].get("state_code") or details["calculated_postcode"] or "",
                    "name": details["addresstags"].get("state") or data["display_name"].split(", ")[0],
                    "country": {
                        "code": details["country_code"].upper() or details["addresstags"].get("country"),
                        "name": data["display_name"].split(", ")[-1]
                    }
                }
            },
            "coordinate": {
                "latitude": data["lat"],
                "longitude": data["lon"]
            }
        }
        if "timezone" not in location:
            location["timezone"] = self._get_timezone(
                lon=location["coordinate"]["longitude"],
                lat=location["coordinate"]["latitude"])
        return location

    # Device Api
    def device_get(self):
        """ Retrieve all device information from the web backend """
        data = JsonStorageXDG("ovos_device_info.json", subfolder="OpenVoiceOS")
        for k, v in super().device_get().items():
            if k not in data:
                data[k] = v
        return data

    def device_get_settings(self):
        """ Retrieve device settings information from the web backend

        Returns:
            str: JSON string with user configuration information.
        """
        return Configuration()  # TODO format keys or not needed ?

    def device_get_skill_settings_v1(self):
        """ old style bidirectional skill settings api, still available!"""
        # TODO scan skill xdg paths
        return []

    def device_put_skill_settings_v1(self, data=None):
        """ old style bidirectional skill settings api, still available!"""
        # do nothing, skills manage their own settings lifecycle
        return {}

    def device_get_code(self, state=None):
        return "ABCDEF"  # dummy data

    def device_activate(self, state, token,
                        core_version="unknown",
                        platform="unknown",
                        platform_build="unknown",
                        enclosure_version="unknown"):
        data = {"state": state,
                "token": token,
                "coreVersion": core_version,
                "platform": platform,
                "platform_build": platform_build,
                "enclosureVersion": enclosure_version}
        identity = self.admin_pair(state)
        data["uuid"] = data.pop("state")
        data["token"] = self.access_token
        BackendDatabase(self.uuid).update_device_db(data)
        db = JsonStorageXDG("ovos_device_info.json", subfolder="OpenVoiceOS")
        db.update(data)
        db.store()
        return identity

    def device_update_version(self,
                              core_version="unknown",
                              platform="unknown",
                              platform_build="unknown",
                              enclosure_version="unknown"):
        data = {"coreVersion": core_version,
                "platform": platform,
                "platform_build": platform_build,
                "enclosureVersion": enclosure_version,
                "token": self.access_token}
        BackendDatabase(self.uuid).update_device_db(data)
        db = JsonStorageXDG("ovos_device_info.json", subfolder="OpenVoiceOS")
        db.update(data)
        db.store()

    def device_report_metric(self, name, data):
        return self.metrics_upload(name, data)

    def device_get_location(self):
        """ Retrieve device location information from the web backend

        Returns:
            str: JSON string with user location.
        """
        return Configuration().get("location") or {}

    def device_get_oauth_token(self, dev_cred):
        """
            Get Oauth token for dev_credential dev_cred.

            Argument:
                dev_cred:   development credentials identifier

            Returns:
                json string containing token and additional information
        """
        raise self.oauth_get_token(dev_cred)

    def device_get_skill_settings(self):
        """Get the remote skill settings for all skills on this device."""
        # TODO - scan xdg paths ?
        return {}

    def device_upload_skill_metadata(self, settings_meta):
        """Upload skill metadata.

        Args:
            settings_meta (dict): skill info and settings in JSON format
        """
        # Do nothing, skills manage their own settingsmeta.json files
        return

    def device_upload_skills_data(self, data):
        """ Upload skills.json file. This file contains a manifest of installed
        and failed installations for use with the Marketplace.

        Args:
             data: dictionary with skills data from msm
        """
        with JsonStorageXDG("ovos_skills_meta.json", subfolder="OpenVoiceOS") as db:
            db.update(data)

    def device_upload_wake_word_v1(self, audio, params, upload_url=None):
        """ upload precise wake word V1 endpoint - url can be external to backend"""
        return self.dataset_upload_wake_word(audio, params, upload_url)

    def device_upload_wake_word(self, audio, params):
        """ upload precise wake word V2 endpoint - integrated with device api"""
        return self.dataset_upload_wake_word(audio, params)

    # Metrics API
    def metrics_upload(self, name, data):
        """ upload metrics"""
        BackendDatabase(self.uuid).update_metrics_db(name, data)
        return {}

    # Dataset API
    def dataset_upload_wake_word(self, audio, params, upload_url=None):
        """ upload wake word sample - url can be external to backend"""
        if Configuration().get("listener", {}).get('record_wake_words'):
            BackendDatabase(self.uuid).update_ww_db(params)  # update metadata db for ww tagging UI

        upload_url = upload_url or Configuration().get("listener", {}).get("wake_word_upload", {}).get("url")
        if upload_url:
            # upload to arbitrary server
            ww_files = {
                'audio': BytesIO(audio.get_wav_data()),
                'metadata': StringIO(json.dumps(params))
            }
            return self.post(upload_url, files=ww_files)
        return {}

    # Email API
    def email_send(self, title, body, sender):
        """ will raise KeyError if SMTP not configured in mycroft.conf"""
        body += f"\n\nsent by: {sender}"  # append skill_id info to body

        mail_config = self.credentials["email"]

        smtp_config = mail_config["smtp"]
        user = smtp_config["username"]
        pswd = smtp_config["password"]
        host = smtp_config["host"]
        port = smtp_config.get("port", 465)

        recipient = mail_config.get("recipient") or user

        send_smtp(user, pswd,
                  user, recipient,
                  title, body,
                  host, port)

    # OAuth API
    def oauth_get_token(self, dev_cred):
        """
            Get Oauth token for dev_credential dev_cred.

            Argument:
                dev_cred:   development credentials identifier

            Returns:
                json string containing token and additional information
        """
        return JsonStorageXDG("ovos_oauth").get(dev_cred) or {}

    # Admin API
    def admin_pair(self, uuid=None):
        uuid = uuid or str(uuid4())
        # create dummy identity file for third parties expecting it for pairing checks
        identity = {"uuid": uuid,
                    "access": "OVOSdbF1wJ4jA5lN6x6qmVk_QvJPqBQZTUJQm7fYzkDyY_Y=",
                    "refresh": "OVOS66c5SpAiSpXbpHlq9HNGl1vsw_srX49t5tCv88JkhuE=",
                    "expires_at": time.time() + 9999999999}
        # save identity file
        IdentityManager.save(identity)
        return identity

    def admin_set_device_location(self, uuid, loc):
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
        update_mycroft_config({"location": loc})

    def admin_set_device_prefs(self, uuid, prefs):
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
        with JsonStorageXDG("ovos_device_info.json", subfolder="OpenVoiceOS") as db:
            db.update(prefs)
        cfg = dict(prefs)
        cfg["listener"] = {}
        cfg["hotwords"] = {}
        cfg["tts"] = {}
        tts = None
        tts_cfg = {}
        ww = None
        ww_cfg = {}
        if "wake_word" in cfg:
            ww = cfg.pop("wake_word")
        if "ww_config" in cfg:
            ww_cfg = cfg.pop("ww_config")
        if "tts_module" in cfg:
            tts = cfg.pop("tts_module")
        if "tts_config" in cfg:
            tts_cfg = cfg.pop("tts_config")
            if not tts:
                tts = tts_cfg.get("module")
        if tts:
            cfg["tts"]["module"] = tts
            cfg["tts"][tts] = tts_cfg
        if ww:
            cfg["listener"]["wake_word"] = ww
            cfg["hotwords"][ww] = ww_cfg
        update_mycroft_config(cfg)

    def admin_set_device_info(self, uuid, info):
        """
        info = {"opt_in": True,
                "name": "my_device",
                "device_location": "kitchen",
                "email": "notifications@me.com",
                "isolated_skills": False,
                "lang": "en-us"}
        """
        update_mycroft_config({"opt_in": info["opt_in"], "lang": info["lang"]})
        with JsonStorageXDG("ovos_device_info.json", subfolder="OpenVoiceOS") as db:
            db.update(info)

    # STT Api
    def load_stt_plugin(self, config=None, lang=None):
        config = config or get_stt_config(config)
        if lang:
            config["lang"] = lang
        self.stt = OVOSSTTFactory.create(config)

    def stt_get(self, audio, language="en-us", limit=1):
        """ Web API wrapper for performing Speech to Text (STT)

        Args:
            audio (bytes): The recorded audio, as in a FLAC file
            language (str): A BCP-47 language code, e.g. "en-US"
            limit (int): Maximum alternate transcriptions

       """
        if self.stt is None:
            self.load_stt_plugin(lang=language)
        with NamedTemporaryFile() as fp:
            fp.write(audio)
            with AudioFile(fp.name) as source:
                audio = Recognizer().record(source)
        tx = self.stt.execute(audio, language)
        if isinstance(tx, str):
            tx = [tx]
        return tx


class AbstractPartialBackend(OfflineBackend):
    """ helper class that internally delegates unimplemented methods to offline backend implementation
    backends that only provide microservices and no DeviceApi should subclass from here
    """

    def __init__(self, url=None, version="v1", identity_file=None, backend_type=BackendType.OFFLINE, credentials=None):
        super().__init__(url, version, identity_file, credentials)
        self.backend_type = backend_type


if __name__ == "__main__":
    b = OfflineBackend()
    b.load_stt_plugin({"module": "ovos-stt-plugin-vosk"})
    # a = b.geolocation_get("Fafe")
    # a = b.wolfram_full_results("2+2")
    # a = b.wolfram_spoken("what is the speed of light")
    # a = b.owm_get_weather()

    from speech_recognition import Recognizer, AudioFile

    with AudioFile("/home/user/PycharmProjects/selene_api/test/test.wav") as source:
        audio = Recognizer().record(source)

    flac_data = audio.get_flac_data()
    a = b.stt_get(flac_data)

    # a = b.owm_get_weather()
    # a = b.owm_get_daily()
    # a = b.owm_get_hourly()
    # a = b.owm_get_current()
    print(a)
