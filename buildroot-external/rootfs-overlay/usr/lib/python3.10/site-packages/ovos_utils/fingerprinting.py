import platform
import socket
from enum import Enum
from os.path import join, isfile
from ovos_utils.system import is_installed, is_running_from_module, has_screen, \
    get_desktop_environment, search_mycroft_core_location, is_process_running
from ovos_config.meta import is_using_xdg


class MycroftPlatform(str, Enum):
    PICROFT = "picroft"
    BIGSCREEN = "kde"
    OVOS = "OpenVoiceOS"
    HIVEMIND = "HiveMind"
    MARK1 = "mycroft_mark_1"
    MARK2 = "mycroft_mark_2"
    HOLMESV = "HolmesV"
    OLD_HOLMES = "mycroft-lib"
    NEON = "neon_core"
    CHATTERBOX = "chatterbox"
    OTHER = "unknown"


def detect_platform():
    return max(((k, v) for k, v in classify_fingerprint().items()),
               key=lambda k: k[1])[0]


def get_config_fingerprint(config=None):
    if not config:
        from ovos_config.config import read_mycroft_config
        config = read_mycroft_config()
    conf = config
    listener_conf = conf.get("listener", {})
    skills_conf = conf.get("skills", {})
    return {
        "enclosure": conf.get("enclosure", {}).get("platform"),
        "data_dir": conf.get("data_dir"),
        "msm_skills_dir": skills_conf.get("msm", {}).get("directory"),
        "ipc_path": conf.get("ipc_path"),
        "input_device_name": listener_conf.get("device_name"),
        "input_device_index": listener_conf.get("device_index"),
        "default_audio_backend": conf.get("Audio", {}).get("default-backend"),
        "priority_skills": skills_conf.get("priority_skills"),
        "backend_url": conf.get("server", {}).get("url")
    }


def get_platform_fingerprint():
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "system": platform.system(),
        "version": platform.version(),
        "arch": platform.machine(),
        "release": platform.release(),
        "desktop_env": get_desktop_environment(),
        "mycroft_core_location": search_mycroft_core_location(),
        "can_display": has_screen(),
        "is_gui_installed": is_installed("mycroft-gui-app"),
        "is_vlc_installed": is_installed("vlc"),
        "pulseaudio_running": is_process_running("pulseaudio"),
        "core_supports_xdg": core_supports_xdg(),
        "core_version": {
            "version_str": get_mycroft_version(),
            "is_chatterbox_core": is_chatterbox_core(),
            "is_neon_core": is_neon_core(),
            "is_holmes": is_holmes(),
            "is_ovos": is_ovos(),
            "is_mycroft_core": is_mycroft_core()
        }
    }


def get_fingerprint():
    finger = get_platform_fingerprint()
    finger["configuration"] = get_config_fingerprint()
    return finger


def core_supports_xdg():
    if any((is_holmes(), is_chatterbox_core())):
        return True
    return is_using_xdg()


def get_mycroft_version():
    try:
        from mycroft.version import CORE_VERSION_STR
        return CORE_VERSION_STR
    except:
        pass

    root = search_mycroft_core_location()
    if root:
        version_file = join(root, "version", "__init__.py")
        if not isfile(version_file):
            version_file = join(root, "mycroft", "version", "__init__.py")
        if isfile(version_file):
            version = []
            with open(version_file) as f:
                text = f.read()
                version.append(
                    text.split("CORE_VERSION_MAJOR =")[-1].split("\n")[
                        0].strip())
                version.append(
                    text.split("CORE_VERSION_MINOR =")[-1].split("\n")[
                        0].strip())
                version.append(
                    text.split("CORE_VERSION_BUILD =")[-1].split("\n")[
                        0].strip())
                version = ".".join(version)
                if "CORE_VERSION_STR = '.'.join(map(str, " \
                   "CORE_VERSION_TUPLE)) + " in text:
                    version += text.split(
                        "CORE_VERSION_STR = '.'.join(map(str, "
                        "CORE_VERSION_TUPLE)) + ")[-1].split("\n")[0][1:-1]
                return version
        return None


def is_chatterbox_core():
    try:
        import chatterbox
        return True
    except ImportError:
        return False


def is_neon_core():
    try:
        import neon_core
        return True
    except ImportError:
        return False


def is_mycroft_core():
    try:
        import mycroft
        return True
    except ImportError:
        return False

def is_vanilla_mycroft_core():
    return is_mycroft_core() and not is_ovos()


def is_holmes():
    return "HolmesV" in (get_mycroft_version() or "") or is_mycroft_lib()


def is_mycroft_lib():
    return "mycroft-lib" in (get_mycroft_version() or "")


def is_ovos():
    return is_running_from_module("ovos-core")


def classify_platform_print(fingerprint=None):
    fingerprint = fingerprint or get_platform_fingerprint()
    # key, val pairs that indicate a certain platform
    fingerprints = {
        MycroftPlatform.PICROFT: {
            "core_supports_xdg": False,
            "core_version": {'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': False,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.BIGSCREEN: {
            "core_supports_xdg": False,
            "core_version": {'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': False,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.OVOS: {
            "core_supports_xdg": True,
            "core_version": {'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': False,
                             'is_ovos': True,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.MARK1: {
            "core_supports_xdg": False,
            "core_version": {'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': False,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.MARK2: {
            "core_supports_xdg": False,
            "core_version": {'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': False,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.HOLMESV: {
            "core_supports_xdg": True,
            "core_version": {'version_str': '20.8.1(HolmesV)',
                             'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': True,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.OLD_HOLMES: {
            "core_supports_xdg": False,
            "core_version": {'version_str': '20.8.1(mycroft-lib)',
                             'is_chatterbox_core': False,
                             'is_neon_core': False,
                             'is_holmes': True,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.CHATTERBOX: {
            "core_supports_xdg": True,
            "core_version": {'is_chatterbox_core': True,
                             'is_neon_core': False,
                             'is_holmes': True,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.NEON: {
            "core_supports_xdg": True,
            "core_version": {'is_chatterbox_core': False,
                             'is_neon_core': True,
                             'is_holmes': True,
                             'is_ovos': False,
                             'is_mycroft_core': True}
        },
        MycroftPlatform.OTHER: {
            "core_supports_xdg": True
        }
    }

    # score += score * weight (if key matches)
    weights = {
        MycroftPlatform.PICROFT: {},
        MycroftPlatform.BIGSCREEN: {},
        MycroftPlatform.OVOS: {
            "core_supports_xdg": 1.0,
            "core_version": 3.0
        },
        MycroftPlatform.CHATTERBOX: {
            "core_supports_xdg": 1.0,
            "core_version": 3.0
        },
        MycroftPlatform.NEON: {
            "core_supports_xdg": 1.0,
            "core_version": 3.0
        },
        MycroftPlatform.MARK1: {},
        MycroftPlatform.MARK2: {},
        MycroftPlatform.HOLMESV: {
            "core_supports_xdg": 1.0,
            "core_version": 3.0
        },
        MycroftPlatform.OLD_HOLMES: {
            "core_supports_xdg": 1.0,
            "core_version": 3.0
        },
        MycroftPlatform.OTHER: {"core_supports_xdg": 0.01}
    }

    # score -= score * weight (if key does not match)
    negative_weights = {
        MycroftPlatform.PICROFT: {
            "core_supports_xdg": 0.1  # likely to change soon once
            # mycroft-core merges the open PR
        },
        MycroftPlatform.BIGSCREEN: {},
        MycroftPlatform.OVOS: {},
        MycroftPlatform.MARK1: {
            "core_supports_xdg": 0.1  # likely to change soon once
            # mycroft-core merges the open PR
        },
        MycroftPlatform.MARK2: {
            "core_supports_xdg": 0.1  # likely to change soon once
            # mycroft-core merges the open PR
        },
        MycroftPlatform.HOLMESV: {},
        MycroftPlatform.OLD_HOLMES: {},
        MycroftPlatform.OTHER: {}
    }

    key_counts = {e: 0 for e in MycroftPlatform}

    for k, v in fingerprint.items():
        # compare this fingerprint value to known platform features
        for enclosure in MycroftPlatform:
            if enclosure not in fingerprints:
                continue
            count = key_counts[enclosure] or 1
            # key is in fingerprint
            if fingerprints[enclosure].get(k):
                # key matches
                if fingerprints[enclosure].get(k) == v:
                    if k in weights.get(enclosure, []):
                        key_counts[enclosure] += count * weights[enclosure][k]
                # key does not match
                elif k in negative_weights.get(enclosure, []):
                    key_counts[enclosure] -= abs(count) * \
                                             negative_weights[enclosure][k]

    # score platforms
    m = max(v for v in key_counts.values())
    if not m:
        return {k: 0 for k in key_counts}
    return {k: v / m for k, v in key_counts.items()}


def classify_config_print(fingerprint=None):
    fingerprint = fingerprint or get_config_fingerprint()

    # key, val pairs that indicate a certain platform
    fingerprints = {
        MycroftPlatform.PICROFT: {
            'backend_url': 'https://api.mycroft.ai',
            'enclosure': 'picroft'
        },
        MycroftPlatform.BIGSCREEN: {
            'backend_url': 'https://api.mycroft.ai'
        },
        MycroftPlatform.OVOS: {
            'enclosure': 'OpenVoiceOS',
            'data_dir': '/opt/ovos'
        },
        MycroftPlatform.MARK1: {
            'backend_url': 'https://api.mycroft.ai',
            'enclosure': 'mycroft_mark_1',
            "data_dir": "/opt/mycroft"
        },
        MycroftPlatform.MARK2: {
            'backend_url': 'https://api.mycroft.ai',
            'enclosure': 'mycroft_mark_2',
            "data_dir": "/opt/mycroft"
        },
        MycroftPlatform.HOLMESV: {
            "enclosure": "HolmesV"
        },
        MycroftPlatform.OLD_HOLMES: {
            "enclosure": "mycroft-lib"
        },
        MycroftPlatform.CHATTERBOX: {
            'enclosure': 'chatterhat',  # TODO list comparison
            "data_dir": "~/chatterbox",
        },
        MycroftPlatform.NEON: {},
        MycroftPlatform.OTHER: {}
    }

    # score += score * weight (if key matches)
    weights = {
        MycroftPlatform.PICROFT: {
            "enclosure": 1.0,
            'backend_url': 0.5
        },
        MycroftPlatform.BIGSCREEN: {},
        MycroftPlatform.OVOS: {
            "enclosure": 1.0
        },
        MycroftPlatform.CHATTERBOX: {
            "enclosure": 1.0,
            'backend_url': 1.0,
            "data_dir": 1.0
        },
        MycroftPlatform.NEON: {
            "enclosure": 1.0
        },
        MycroftPlatform.MARK1: {
            "enclosure": 1.0,
            'backend_url': 1.0,
            "data_dir": 1.0
        },
        MycroftPlatform.MARK2: {
            "enclosure": 1.0,
            'backend_url': 1.0,
            "data_dir": 1.0
        },
        MycroftPlatform.HOLMESV: {},
        MycroftPlatform.OTHER: {}
    }

    # score -= score * weight (if key does not match)
    negative_weights = {
        MycroftPlatform.PICROFT: {
            "enclosure": 0.2,
            'backend_url': 0.2
        },
        MycroftPlatform.BIGSCREEN: {},
        MycroftPlatform.OVOS: {},
        MycroftPlatform.MARK1: {
            "enclosure": 3.0,
            'backend_url': 0.5,
            'data_dir': 1.0
        },
        MycroftPlatform.MARK2: {
            "enclosure": 3.0,
            'backend_url': 0.5,
            'data_dir': 1.5  # pantacor really needs /opt, users cant change it
        },
        MycroftPlatform.HOLMESV: {},
        MycroftPlatform.OLD_HOLMES: {"enclosure": 0.5},
        MycroftPlatform.OTHER: {}
    }

    key_counts = {e: 0 for e in MycroftPlatform}

    for k, v in fingerprint.items():
        # compare this fingerprint value to known platform features
        for enclosure in MycroftPlatform:
            count = key_counts[enclosure] or 1
            # key is in fingerprint
            if fingerprints[enclosure].get(k):

                # key matches
                if fingerprints[enclosure][k] == v:
                    if k in weights.get(enclosure, []):
                        key_counts[enclosure] += count * weights[enclosure][k]
                # key does not match
                elif k in negative_weights.get(enclosure, []):
                    key_counts[enclosure] -= abs(count) * \
                                             negative_weights[enclosure][k]

    # score platforms
    m = max(v for v in key_counts.values())
    if not m:
        return {k: 0 for k in key_counts}
    return {k: v / m for k, v in key_counts.items()}


def classify_fingerprint():
    plat = classify_platform_print()
    conf = classify_config_print()
    for k, v in conf.items():
        # high bias for platform fingerprint
        plat[k] = (v * 0.5 + plat[k] * 1.5) / 2
    return plat
