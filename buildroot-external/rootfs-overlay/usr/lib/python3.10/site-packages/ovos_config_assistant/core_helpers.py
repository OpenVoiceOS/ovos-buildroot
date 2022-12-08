import json
from os.path import join, expanduser

from ovos_utils.json_helper import merge_dict
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_config_home


def setup_neon(core_path="~/NeonCore"):
    """
    setup config for NeonCore
    """
    OVOS_CONFIG = join(xdg_config_home(), "OpenVoiceOS", "ovos.conf")
    _NEON_OVOS_CONFIG = {
        "module_overrides": {
            "neon_core": {
                "xdg": True,
                "base_folder": "neon",
                "config_filename": "neon.conf",
                "default_config_path": join(expanduser(core_path), "neon_core", 'configuration', 'neon.conf')
            }
        },
        # if these services are running standalone (neon_core not in venv)
        # config them to use neon_core config from above
        "submodule_mappings": {
            "neon_speech": "neon_core",
            "neon_audio": "neon_core",
            "neon_enclosure": "neon_core"
        }
    }

    cfg = {}
    try:
        with open(OVOS_CONFIG) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        pass
    except Exception as e:
        LOG.error(e)

    cfg = merge_dict(cfg, _NEON_OVOS_CONFIG)
    with open(OVOS_CONFIG, "w") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=True)


def setup_hivemind():
    """
    setup config for LocalHive
    """
    OVOS_CONFIG = join(xdg_config_home(), "OpenVoiceOS", "ovos.conf")

    _NEW_OVOS_CONFIG = {
        "module_overrides": {
            "hivemind": {
                "xdg": True,
                "base_folder": "hivemind",
                "config_filename": "hivemind.conf"
            }
        },
        # if these services are running standalone (core not in venv)
        # config them to use core config from above
        "submodule_mappings": {
            "hivemind_voice_satellite": "hivemind"
        }
    }

    cfg = {}
    try:
        with open(OVOS_CONFIG) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        pass
    except Exception as e:
        LOG.error(e)

    cfg = merge_dict(cfg, _NEW_OVOS_CONFIG)
    with open(OVOS_CONFIG, "w") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=True)


def setup_chatterbox():
    """
    setup config for chatterbox
    """
    OVOS_CONFIG = join(xdg_config_home(), "OpenVoiceOS", "ovos.conf")
    _NEW_OVOS_CONFIG = {
        "module_overrides": {
            "chatterbox": {
                "xdg": False,
                "base_folder": "chatterbox",
                "config_filename": "chatterbox.conf",
                "default_config_path": "/opt/chatterbox/chatterbox.conf"
            }
        },
        # if these services are running standalone (core not in venv)
        # config them to use core config from above
        "submodule_mappings": {
            "chatterbox_playback": "chatterbox",
            "chatterbox_stt": "chatterbox",
            "chatterbox_blockly": "chatterbox",
            "chatterbox_admin": "chatterbox",
            "chatterbox_gpio_service": "neon_core"
        }
    }
    cfg = {}
    try:
        with open(OVOS_CONFIG) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        pass
    except Exception as e:
        LOG.error(e)

    cfg = merge_dict(cfg, _NEW_OVOS_CONFIG)
    with open(OVOS_CONFIG, "w") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=True)
