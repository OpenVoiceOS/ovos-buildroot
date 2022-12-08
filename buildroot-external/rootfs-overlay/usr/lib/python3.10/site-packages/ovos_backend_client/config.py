import re
from pprint import pformat

from ovos_utils import camel_case_split
from ovos_utils.log import LOG

from ovos_backend_client.api import DeviceApi
from ovos_backend_client.pairing import is_paired
from ovos_backend_client.identity import IdentityManager


def _is_remote_list(values):
    """Check if list corresponds to a backend formatted collection of dicts
    """
    for v in values:
        if not isinstance(v, dict):
            return False
        if "@type" not in v.keys():
            return False
    return True


def _translate_remote(config, setting):
    """Translate config names from server to equivalents for mycroft-core.

    Args:
        config:     base config to populate
        settings:   remote settings to be translated
    """
    IGNORED_SETTINGS = ["uuid", "@type", "active", "user", "device"]

    for k, v in setting.items():
        if k not in IGNORED_SETTINGS:
            # Translate the CamelCase values stored remotely into the
            # Python-style names used within mycroft-core.
            key = re.sub(r"Setting(s)?", "", k)
            key = camel_case_split(key).replace(" ", "_").lower()
            if isinstance(v, dict):
                config[key] = config.get(key, {})
                _translate_remote(config[key], v)
            elif isinstance(v, list):
                if _is_remote_list(v):
                    if key not in config:
                        config[key] = {}
                    _translate_list(config[key], v)
                else:
                    config[key] = v
            else:
                config[key] = v


def _translate_list(config, values):
    """Translate list formatted by mycroft server.

    Args:
        config (dict): target config
        values (list): list from mycroft server config
    """
    for v in values:
        module = v["@type"]
        if v.get("active"):
            config["module"] = module
        config[module] = config.get(module, {})
        _translate_remote(config[module], v)


class RemoteConfigManager:
    """Config dictionary fetched from mycroft.ai."""

    def __init__(self, url=None, version="v1", identity_file=None):
        self.api = DeviceApi(url, version, identity_file)
        self.config = {"server": {"disabled": True}}

    def download(self):
        if not is_paired(url=self.api.backend_url,
                         version=self.api.backend_version,
                         identity_file=IdentityManager.IDENTITY_FILE):
            self.config = {"server": {"disabled": True}}
            return
        else:
            self.config["server"]["disabled"] = False

        try:
            remote = self.api.get_settings()

            try:  # this call is unnecessary in personal backend but needed in selene
                location = self.api.get_location()
                remote["location"] = location
            except Exception as e:
                LOG.error(f"Exception fetching remote location: {e}")

            # Remove server specific entries
            _translate_remote(self.config, remote)

        except Exception as e:
            LOG.error(f"Exception fetching remote configuration: {e}")

    def print(self):
        print(pformat(self.config))


if __name__ == "__main__":
    cfg = RemoteConfigManager()
    cfg.download()
    cfg.print()
    # {'date_format': 'DMY',
    #  'hotwords': {'hey_mycroft': {'module': 'ovos-ww-plugin-pocketsphinx',
    #                               'phonemes': 'HH EY . M AY K R AO F T',
    #                               'threshold': 1e-90}},
    #  'listener': {'wake_word': 'hey_mycroft'},
    #  'location': {'city': {'code': 'Porto',
    #                        'name': 'Porto',
    #                        'region': {'code': '13',
    #                                   'country': {'code': 'PT', 'name': 'Portugal'},
    #                                   'name': 'Porto'},
    #                        'state': {'code': '13',
    #                                  'country': {'code': 'PT', 'name': 'Portugal'},
    #                                  'name': 'Porto'}},
    #               'coordinate': {'latitude': 41.1691, 'longitude': -8.6793},
    #               'timezone': {'code': 'Europe/Lisbon',
    #                            'dst_offset': 3600000,
    #                            'name': 'Europe/Lisbon',
    #                            'offset': -21600000}},
    #  'opt_in': False,
    #  'server': {'disabled': False},
    #  'system_unit': 'metric',
    #  'time_format': 'full',
    #  'tts': {'module': 'ovos-tts-plugin-mimic2',
    #          'ovos-tts-plugin-mimic2': {'module': 'ovos-tts-plugin-mimic2',
    #                                     'voice': 'kusal'}}}
