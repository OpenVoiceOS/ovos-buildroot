import json
import os
import time
from io import BytesIO, StringIO

from ovos_config.config import Configuration
from ovos_utils.log import LOG
from requests.exceptions import HTTPError

from ovos_backend_client.backends.offline import AbstractPartialBackend, BackendType
from ovos_backend_client.identity import IdentityManager, identity_lock
import requests


class PersonalBackend(AbstractPartialBackend):

    def __init__(self, url="http://0.0.0.0:6712", version="v1", identity_file=None, credentials=None):
        super().__init__(url, version, identity_file, BackendType.PERSONAL, credentials)

    def refresh_token(self):
        try:
            identity_lock.acquire(blocking=False)
            # NOTE: requests needs to be used instead of self.get due to self.get calling this
            data = requests.get(f"{self.backend_url}/{self.backend_version}/auth/token", headers=self.headers).json()
            IdentityManager.save(data, lock=False)
            LOG.debug('Saved credentials')
        except:
            LOG.warning("Failed to refresh access token")
        finally:
            try:
                identity_lock.release()
            except RuntimeError:  # RuntimeError: release unlocked lock
                pass

    # OWM Api
    def owm_get_weather(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location
        lat, lon = lat_lon or self._get_lat_lon()
        response = self.get(url=f"{self.backend_url}/{self.backend_version}/owm/onecall",
                            params={
                                "lang": self.owm_language(lang),
                                "lat": lat,
                                "lon": lon,
                                "units": units})
        return response.json()

    def owm_get_current(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location
        lat, lon = lat_lon or self._get_lat_lon()
        response = self.get(url=f"{self.backend_url}/{self.backend_version}/owm/weather",
                            params={
                                "lang": self.owm_language(lang),
                                "lat": lat,
                                "lon": lon,
                                "units": units})
        return response.json()

    def owm_get_hourly(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location
        lat, lon = lat_lon or self._get_lat_lon()
        response = self.get(url=f"{self.backend_url}/{self.backend_version}/owm/forecast",
                            params={
                                "lang": self.owm_language(lang),
                                "lat": lat,
                                "lon": lon,
                                "units": units})
        return response.json()

    def owm_get_daily(self, lat_lon=None, lang="en-us", units="metric"):
        """Issue an API call and map the return value into a weather report

        Args:
            units (str): metric or imperial measurement units
            lat_lon (tuple): the geologic (latitude, longitude) of the weather location
        """
        # default to configured location
        lat, lon = lat_lon or self._get_lat_lon()
        response = self.get(url=f"{self.backend_url}/{self.backend_version}/owm/forecast/daily",
                            params={
                                "lang": self.owm_language(lang),
                                "lat": lat,
                                "lon": lon,
                                "units": units})
        return response.json()

    # Wolfram Alpha API
    def wolfram_spoken(self, query, units="metric", lat_lon=None, optional_params=None):
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'i': query,
                  "geolocation": "{},{}".format(*lat_lon),
                  'units': units,
                  **optional_params}
        url = f"{self.backend_url}/{self.backend_version}/wolframAlphaSpoken"
        data = self.get(url=url, params=params)
        return data.text

    def wolfram_simple(self, query, units="metric", lat_lon=None, optional_params=None):
        optional_params = optional_params or {}
        if not lat_lon:
            lat_lon = self._get_lat_lon(**optional_params)
        params = {'i': query,
                  "geolocation": "{},{}".format(*lat_lon),
                  'units': units,
                  **optional_params}
        url = f"{self.backend_url}/{self.backend_version}/wolframAlphaSimple"
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
        url = f"{self.backend_url}/{self.backend_version}/wolframAlphaFull"
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
        url = f"{self.backend_url}/{self.backend_version}/geolocation"
        location = self.get(url, params={"location": location}).json()['data']
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

        Returns:
            dict: JSON structure with transcription results
        """
        data = self.post(url=f"{self.backend_url}/{self.backend_version}/stt",
                         data=audio, params={"lang": language, "limit": limit},
                         headers={"Content-Type": "audio/x-flac"})
        if data.status_code == 200:
            return data.json()
        raise RuntimeError(f"STT api failed, status_code {data.status_code}")

    # Device Api
    def device_get(self):
        """ Retrieve all device information from the web backend """
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}").json()

    def device_get_settings(self):
        """ Retrieve device settings information from the web backend

        Returns:
            str: JSON string with user configuration information.
        """
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/setting").json()

    def device_get_skill_settings_v1(self):
        """ old style bidirectional skill settings api, still available!"""
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/skill").json()

    def device_put_skill_settings_v1(self, data=None):
        """ old style bidirectional skill settings api, still available!"""
        self.put(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/skill", json=data)

    def device_get_code(self, state=None):
        state = state or self.uuid
        return self.get(f"{self.backend_url}/{self.backend_version}/device/code", params={"state": state}).json()

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
        r = self.post(f"{self.backend_url}/{self.backend_version}/device/activate", json=data)
        try:
            return r.json()
        except:
            # raise expected exception handled by pairing manager, any other resets pairing process
            raise HTTPError(f"Device activation failed! {r.status_code}")

    def device_update_version(self,
                              core_version="unknown",
                              platform="unknown",
                              platform_build="unknown",
                              enclosure_version="unknown"):
        data = {"coreVersion": core_version,
                "platform": platform,
                "platform_build": platform_build,
                "enclosureVersion": enclosure_version}
        return self.patch(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}", json=data)

    def device_report_metric(self, name, data):
        return self.post(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/metric/" + name,
                         json=data)

    def device_get_location(self):
        """ Retrieve device location information from the web backend

        Returns:
            str: JSON string with user location.
        """
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/location").json()

    def device_get_subscription(self):
        """
            Get information about type of subscription this unit is connected
            to.

            Returns: dictionary with subscription information
        """
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/subscription").json()

    def device_get_subscriber_voice_url(self, voice=None, arch=None):
        archs = {'x86_64': 'x86_64', 'armv7l': 'arm', 'aarch64': 'arm'}
        arch = arch or archs.get(os.uname()[4])
        if arch:
            url = f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/voice"
            return self.get(url, params={"arch": arch}).json().get('link')

    def device_get_oauth_token(self, dev_cred):
        """
            Get Oauth token for dev_credential dev_cred.

            Argument:
                dev_cred:   development credentials identifier

            Returns:
                json string containing token and additional information
        """
        return self.oauth_get_token(dev_cred)

    def device_get_skill_settings(self):
        """Get the remote skill settings for all skills on this device."""
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/skill/settings").json()

    def device_send_email(self, title, body, sender):
        return self.put(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/message",
                        json={"title": title, "body": body, "sender": sender}).json()

    def device_upload_skill_metadata(self, settings_meta):
        """Upload skill metadata.

        Args:
            settings_meta (dict): skill info and settings in JSON format
        """
        return self.put(url=f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/settingsMeta",
                        json=settings_meta)

    def device_upload_skills_data(self, data):
        """ Upload skills.json file. This file contains a manifest of installed
        and failed installations for use with the Marketplace.

        Args:
             data: dictionary with skills data from msm
        """
        return self.put(url=f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/skillJson",
                        json=data)

    def device_upload_wake_word_v1(self, audio, params, upload_url=None):
        """ upload precise wake word V1 endpoint - url can be external to backend"""
        if not upload_url:
            config = Configuration().get("listener", {}).get("wake_word_upload", {})
            upload_url = config.get("url") or f"{self.backend_url}/precise/upload"
        ww_files = {
            'audio': BytesIO(audio.get_wav_data()),
            'metadata': StringIO(json.dumps(params))
        }
        return self.post(upload_url, files=ww_files)

    def device_upload_wake_word(self, audio, params):
        """ upload precise wake word V2 endpoint - integrated with device api"""
        url = f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/wake-word-file"
        request_data = dict(
            wake_word=params['name'],
            engine=params.get('engine_name') or params.get('engine'),
            timestamp=params.get('timestamp') or params.get('time') or str(int(1000 * time.time())),
            model=params['model']
        )
        ww_files = {
            'audio': BytesIO(audio.get_wav_data()),
            'metadata': StringIO(json.dumps(request_data))
        }
        return self.post(url, files=ww_files)

    # Metrics API
    def metrics_upload(self, name, data):
        """ upload metrics"""
        return self.device_report_metric(name, data)

    # Dataset API
    def dataset_upload_wake_word(self, audio, params, upload_url=None):
        """ upload wake word sample - url can be external to backend"""
        if upload_url:  # explicit upload endpoint requested
            return self.device_upload_wake_word_v1(audio, params, upload_url)
        return self.device_upload_wake_word(audio, params)

    # OAuth API
    def oauth_get_token(self, dev_cred):
        """
            Get Oauth token for dev_credential dev_cred.

            Argument:
                dev_cred:   development credentials identifier

            Returns:
                json string containing token and additional information
        """
        return self.get(f"{self.backend_url}/{self.backend_version}/device/{self.uuid}/token/{dev_cred}").json()

    # Email API
    def email_send(self, title, body, sender):
        return self.device_send_email(title, body, sender)

    # Admin API
    def admin_pair(self, uuid=None):
        identity = self.get(f"{self.backend_url}/{self.backend_version}/admin/{uuid}/pair",
                            headers={"Authorization": f"Bearer {self.credentials['admin']}"})
        # save identity file
        self.identity.save(identity)
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
        return self.put(f"{self.backend_url}/{self.backend_version}/admin/{uuid}/location", json=loc,
                        headers={"Authorization": f"Bearer {self.credentials['admin']}"})

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
        return self.put(f"{self.backend_url}/{self.backend_version}/admin/{uuid}/prefs", json=prefs,
                        headers={"Authorization": f"Bearer {self.credentials['admin']}"})

    def admin_set_device_info(self, uuid, info):
        """
        info = {"opt_in": True,
                "name": "my_device",
                "device_location": "kitchen",
                "email": "notifications@me.com",
                "isolated_skills": False,
                "lang": "en-us"}
        """
        return self.put(f"{self.backend_url}/{self.backend_version}/admin/{uuid}/device", json=info,
                        headers={"Authorization": f"Bearer {self.credentials['admin']}"})
