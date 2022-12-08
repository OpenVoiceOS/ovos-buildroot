from ovos_config.config import Configuration

from ovos_backend_client.backends.base import BackendType
from ovos_backend_client.backends.offline import OfflineBackend
from ovos_backend_client.backends.ovos import OVOS_API_URL, OVOSAPIBackend
from ovos_backend_client.backends.personal import PersonalBackend
from ovos_backend_client.backends.selene import SELENE_API_URL, SeleneBackend

API_REGISTRY = {
    BackendType.OFFLINE: {
        "admin": True,  # updates mycroft.conf if used
        "device": True,  # shared database with local backend for UI compat
        "dataset": True,  # shared database with local backend for ww tagger UI compat
        "metrics": True,  # shared database with local backend for metrics UI compat
        "wolfram": True,  # key needs to be set
        "geolocate": True,  # nominatim - no key needed
        "stt": True,  # uses OPM and reads from mycroft.conf
        "owm": True,  # key needs to be set
        "email": True,  # smtp config needs to be set
        "oauth": True  # use local backend UI on same device to register apps
    },
    BackendType.SELENE: {
        "admin": False,
        "device": True,
        "dataset": True,
        "metrics": True,
        "wolfram": True,
        "geolocate": True,
        "stt": True,
        "owm": True,
        "email": True,  # only send to email used for registering account
        "oauth": True
    },
    BackendType.PERSONAL: {
        "admin": True,
        "device": True,
        "dataset": True,
        "metrics": True,
        "wolfram": True,
        "geolocate": True,
        "stt": True,
        "owm": True,
        "email": True,
        "oauth": True  # can use local backend UI to register apps
    },
    BackendType.OVOS_API: {
        "admin": True,  # fake support -> cast to offline backend type
        "device": True,  # fake support -> cast to offline backend type
        "dataset": True,  # fake support -> cast to offline backend type
        "metrics": True,  # fake support -> cast to offline backend type
        "wolfram": True,
        "geolocate": True,
        "stt": True,
        "owm": True,
        "email": True,
        "oauth": True  # fake support -> cast to offline backend type
    }
}


def get_backend_type(conf=None):
    conf = conf or Configuration()
    if "server" in conf:
        conf = conf["server"]
    if conf.get("disabled"):
        return BackendType.OFFLINE
    if "backend_type" in conf:
        return conf["backend_type"]
    url = conf.get("url")
    if not url:
        return BackendType.OFFLINE
    if "api.openvoiceos.com" in url:
        return BackendType.OVOS_API
    elif "mycroft.ai" in url:
        return BackendType.SELENE
    return BackendType.PERSONAL


def get_backend_config(url=None, version="v1", identity_file=None, backend_type=None):
    config = Configuration()
    config_server = config.get("server") or {}
    if not url:
        url = config_server.get("url")
        version = config_server.get("version") or version
        backend_type = backend_type or get_backend_type(config)
    elif not backend_type:
        backend_type = get_backend_type({"url": url})

    if not url and backend_type:
        if backend_type == BackendType.SELENE:
            url = SELENE_API_URL
        elif backend_type == BackendType.OVOS_API:
            url = OVOS_API_URL
        elif backend_type == BackendType.PERSONAL:
            url = "http://0.0.0.0:6712"
        else:
            url = "http://127.0.0.1"

    return url, version, identity_file, backend_type
