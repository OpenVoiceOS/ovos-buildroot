from ovos_plugin_manager.utils import load_plugin, normalize_lang, find_plugins, PluginTypes, PluginConfigTypes
from ovos_config import Configuration
from ovos_plugin_manager.utils.config import get_valid_plugin_configs, sort_plugin_configs
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.stt import STT, StreamingSTT, StreamThread


def find_stt_plugins():
    return find_plugins(PluginTypes.STT)


def get_stt_configs() -> dict:
    """
    Get a dict of plugin names to valid STT configuration
    @return: dict plugin name to dict of str lang to list of dict valid configs
    """
    return {plug: get_stt_module_configs(plug)
            for plug in find_stt_plugins()}


def get_stt_module_configs(module_name: str) -> dict:
    """
    Get a dict of lang to list of valid config dicts for a specific plugin
    @param module_name: name of plugin to get configurations for
    @return: {lang: [list of config dicts]}
    """
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.STT) or {}
    configs = {normalize_lang(lang): v for lang, v in cfgs.items()}
    # let's sort by priority key
    for k, v in configs.items():
        configs[k] = sorted(v, key=lambda c: c.get("priority", 60))
    return configs


def get_stt_lang_configs(lang: str, include_dialects: bool = False) -> dict:
    """
    Get a dict of plugins names to sorted list of valid configurations
    @param lang: language to get configurations for (i.e. en, en-US)
    @param include_dialects: If true, include configs for other locales
        (i.e. include en-GB configs for lang=en-US)
    @return: dict plugin name to list of valid configs sorted by priority
    """
    lang = normalize_lang(lang)
    matched_configs = {}
    for plug in find_stt_plugins():
        matched_configs[plug] = []
        confs = get_stt_module_configs(plug)
        matched_configs[plug] = get_valid_plugin_configs(confs, lang,
                                                         include_dialects)
    return sort_plugin_configs(matched_configs)


def get_stt_supported_langs() -> dict:
    """
    Get a dict of languages to valid configuration options
    @return: dict lang to list of plugins that support that lang
    """
    configs = {}
    for plug in find_stt_plugins():
        confs = get_stt_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_stt_plugin(module_name):
    """Wrapper function for loading stt plugin.

    Arguments:
        module_name (str): Mycroft stt module name from config
    Returns:
        class: STT plugin class
    """
    return load_plugin(module_name, PluginTypes.STT)


class OVOSSTTFactory:
    """ replicates the base mycroft class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "mycroft": "ovos-stt-plugin-selene",
        "dummy": "ovos-stt-plugin-dummy",
        "google": "ovos-stt-plugin-chromium",
        #    "google_cloud": GoogleCloudSTT,
        #    "google_cloud_streaming": GoogleCloudStreamingSTT,
        #    "wit": WITSTT,
        #    "ibm": IBMSTT,
        #    "kaldi": KaldiSTT,
        #    "bing": BingSTT,
        #    "govivace": GoVivaceSTT,
        #    "houndify": HoundifySTT,
        #    "deepspeech_server": DeepSpeechServerSTT,
        #    "deepspeech_stream_server": DeepSpeechStreamServerSTT,
        #    "mycroft_deepspeech": MycroftDeepSpeechSTT,
        #    "yandex": YandexSTT
        "vosk": "ovos-stt-plugin-vosk",
        "vosk_streaming": "ovos-stt-plugin-vosk-streaming"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a STT engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``stt`` section with
        the name of a STT module to be read by this method.

        "stt": {
            "module": <engine_name>
        }
        """
        config = config or get_stt_config()
        stt_module = config["module"]
        if stt_module in OVOSSTTFactory.MAPPINGS:
            stt_module = OVOSSTTFactory.MAPPINGS[stt_module]
        return load_stt_plugin(stt_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a STT engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``stt`` section with
        the name of a STT module to be read by this method.

        "stt": {
            "module": <engine_name>
        }
        """
        config = get_stt_config(config)
        plugin = config["module"]
        plugin_config = config.get(plugin) or {}
        try:
            clazz = OVOSSTTFactory.get_class(config)
            return clazz(plugin_config)
        except Exception:
            LOG.exception('The selected STT plugin could not be loaded!')
            raise


def get_stt_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    stt_config = get_plugin_config(config, "stt")
    stt_config.setdefault("lang", "en-us")
    return stt_config
