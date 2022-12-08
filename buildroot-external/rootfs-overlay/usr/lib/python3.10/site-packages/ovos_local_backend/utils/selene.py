import json
from uuid import uuid4

from flask import request
from ovos_utils.log import LOG
from ovos_backend_client.api import DeviceApi, STTApi
from ovos_backend_client.identity import IdentityManager
from ovos_backend_client.pairing import has_been_paired

from ovos_local_backend.configuration import CONFIGURATION, BACKEND_IDENTITY
from ovos_local_backend.database.settings import SkillSettings, SharedSettingsDatabase, DeviceDatabase

_selene_pairing_data = None
_selene_uuid = str(uuid4())
_selene_cfg = CONFIGURATION.get("selene") or {}

_ident_file = _selene_cfg.get("identity_file", "")
if _ident_file != IdentityManager.IDENTITY_FILE:
    IdentityManager.set_identity_file(_ident_file)

_device_api = DeviceApi(_selene_cfg.get("url"),
                        _selene_cfg.get("version") or "v1",
                        _selene_cfg.get("identity_file"))


def upload_selene_skill_settings(settings):
    selene_cfg = CONFIGURATION.get("selene") or {}
    url = selene_cfg.get("url")
    version = selene_cfg.get("version") or "v1"
    identity_file = selene_cfg.get("identity_file")
    if selene_cfg.get("enabled"):
        # upload settings to selene if enabled
        api = DeviceApi(url, version, identity_file)
        api.put_skill_settings_v1(settings)


def upload_selene_skill_settingsmeta(meta):
    selene_cfg = CONFIGURATION.get("selene") or {}
    url = selene_cfg.get("url")
    version = selene_cfg.get("version") or "v1"
    identity_file = selene_cfg.get("identity_file")
    if selene_cfg.get("enabled"):
        # upload settings to selene if enabled
        api = DeviceApi(url, version, identity_file)
        api.upload_skill_metadata(meta)


def download_selene_skill_settings():
    selene_cfg = CONFIGURATION.get("selene") or {}
    if selene_cfg.get("enabled"):
        url = selene_cfg.get("url")
        version = selene_cfg.get("version") or "v1"
        identity_file = selene_cfg.get("identity_file")
        # get settings from selene if enabled
        api = DeviceApi(url, version, identity_file)
        sets = api.get_skill_settings()
        for skill_id, s in sets.items():
            s = SkillSettings.deserialize(s)
            # sync local db with selene
            with SharedSettingsDatabase() as db:
                db.add_setting(s.skill_id, s.settings, s.meta,
                               s.display_name, s.remote_id)


def download_selene_location(uuid):
    # get location from selene if enabled
    selene_cfg = CONFIGURATION.get("selene") or {}
    if selene_cfg.get("enabled"):
        url = selene_cfg.get("url")
        version = selene_cfg.get("version") or "v1"
        identity_file = selene_cfg.get("identity_file")
        api = DeviceApi(url, version, identity_file)
        # update in local db
        loc = api.get_location()
        with DeviceDatabase() as db:
            device = db.get_device(uuid)
            device.location = loc
            db.update_device(device)


def download_selene_preferences(uuid):
    # get location from selene if enabled
    selene_cfg = CONFIGURATION.get("selene") or {}
    if selene_cfg.get("enabled"):
        url = selene_cfg.get("url")
        version = selene_cfg.get("version") or "v1"
        identity_file = selene_cfg.get("identity_file")
        api = DeviceApi(url, version, identity_file)
        data = api.get_settings()
        # update in local db
        with DeviceDatabase() as db:
            device = db.get_device(uuid)
            device.system_unit = data["systemUnit"]
            device.time_format = data["timeFormat"]
            device.date_format = data["dateFormat"]
            db.update_device(device)


def send_selene_email(title, body, sender):
    selene_cfg = CONFIGURATION.get("selene") or {}
    url = selene_cfg.get("url")
    version = selene_cfg.get("version") or "v1"
    identity_file = selene_cfg.get("identity_file")
    api = DeviceApi(url, version, identity_file)
    return api.send_email(title, body, sender)


def report_selene_metric(name, data):
    # contribute to mycroft metrics dataset
    selene_cfg = CONFIGURATION.get("selene") or {}
    if selene_opted_in():
        url = selene_cfg.get("url")
        version = selene_cfg.get("version") or "v1"
        identity_file = selene_cfg.get("identity_file")
        api = DeviceApi(url, version, identity_file)
        return api.report_metric(name, data)
    return {"success": True, "metric": data, "upload_data": {"uploaded": False}}


def upload_utterance(audio, lang="en-us"):
    selene_cfg = CONFIGURATION.get("selene") or {}
    if selene_opted_in():
        url = selene_cfg.get("url")
        version = selene_cfg.get("version") or "v1"
        identity_file = selene_cfg.get("identity_file")
        api = STTApi(url, version, identity_file)
        api.stt(audio, lang)


def upload_ww(files):
    audio = None
    meta = {}

    for precisefile in files:
        fn = files[precisefile].filename
        if fn == 'audio':
            audio = files[precisefile].stream.read()
        if fn == 'metadata':
            meta = json.load(files[precisefile].stream)

    uploaded = False
    if audio and selene_opted_in():
        # contribute to mycroft open dataset
        api = DeviceApi()
        try:
            # old endpoint - supported by all local backend versions
            # not sure if still supported by selene ?
            api.upload_wake_word_v1(audio, meta)
        except:
            # new selene endpoint, not sure if already live ?
            api.upload_wake_word(audio, meta)
    return uploaded


def selene_opted_in():
    if not _selene_cfg.get("enabled") or not _selene_cfg.get("opt_in"):
        return False
    auth = request.headers.get('Authorization', '').replace("Bearer ", "")
    uuid = auth.split(":")[-1]  # this split is only valid here, not selene
    if uuid in _selene_cfg.get("opt_in_blacklist", []):
        return False
    # check device db for per-device opt_in settings
    device = DeviceDatabase().get_device(uuid)
    if not device or not device.opt_in:
        return False
    return True


def requires_selene_pairing(func_name):
    enabled = _selene_cfg.get("enabled")
    check_pairing = False
    if enabled:
        # identity file settings
        check_pairing = True

        # individual selene integration settings
        if "wolfie" in func_name and not _selene_cfg.get("proxy_wolfram"):
            check_pairing = False
        elif "owm" in func_name and not _selene_cfg.get("proxy_weather"):
            check_pairing = False
        elif func_name == "geolocation" and not _selene_cfg.get("proxy_geolocation"):
            check_pairing = False
        elif func_name == "send_mail" and not _selene_cfg.get("proxy_email"):
            check_pairing = False
        elif func_name == "location" and not _selene_cfg.get("download_location"):
            check_pairing = False
        elif func_name == "setting" and not _selene_cfg.get("download_prefs"):
            check_pairing = False
        elif func_name == "settingsmeta" and not _selene_cfg.get("upload_settings"):
            check_pairing = False
        elif "skill_settings" in func_name:
            if request.method == 'PUT':
                if not _selene_cfg.get("upload_settings"):
                    check_pairing = False
            elif not _selene_cfg.get("download_settings"):
                check_pairing = False

        # check opt in settings
        opts = ["precise_upload", "stt", "metric"]
        if not selene_opted_in() and func_name in opts:
            check_pairing = False
        else:
            if func_name == "precise_upload" and not _selene_cfg.get("upload_wakewords"):
                check_pairing = False
            if func_name == "stt" and not _selene_cfg.get("upload_utterances"):
                check_pairing = False
            if func_name == "metric" and not _selene_cfg.get("upload_metrics"):
                check_pairing = False

    return check_pairing


def get_selene_code():
    _selene_pairing_data = get_selene_pairing_data()
    return _selene_pairing_data.get("code")


def get_selene_pairing_data():
    global _selene_pairing_data, _selene_uuid
    if not _selene_pairing_data:
        try:
            _selene_uuid = str(uuid4())
            _selene_pairing_data = _device_api.get_code(_selene_uuid)
        except:
            LOG.exception("Failed to get selene pairing data")
    return _selene_pairing_data or {}


def attempt_selene_pairing():
    global _selene_pairing_data
    backend_version = "0.0.1"
    platform = "ovos-local-backend"
    ident_file = _selene_cfg.get("identity_file") or BACKEND_IDENTITY
    if ident_file != IdentityManager.IDENTITY_FILE:
        IdentityManager.set_identity_file(ident_file)
    if _selene_cfg.get("enabled") and not has_been_paired():
        data = get_selene_pairing_data()
        if data:
            tok = data["token"]
            try:
                login = _device_api.activate(_selene_uuid, tok,
                                             platform=platform,
                                             platform_build=backend_version,
                                             core_version=backend_version,
                                             enclosure_version=backend_version)
                try:
                    IdentityManager.save(login)
                except:
                    LOG.exception("Failed to save identity, restarting pairing")
                    _selene_pairing_data = None
            except:
                LOG.exception("Failed to activate with selene, user did not yet enter pairing code")
