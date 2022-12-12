from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.hotwords import HotWordEngine


def find_wake_word_plugins():
    return find_plugins(PluginTypes.WAKEWORD)


def get_ww_configs():
    configs = {}
    for plug in find_wake_word_plugins():
        configs[plug] = get_ww_module_configs(plug)
    return configs


def get_ww_module_configs(module_name):
    # WW plugins return {ww_name: [list of config dicts]}
    return load_plugin(module_name + ".config", PluginConfigTypes.WAKEWORD) or {}


def get_ww_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_wake_word_plugins():
        configs[plug] = []
        confs = get_ww_module_configs(plug)
        for ww_name, ww_conf in confs.items():
            ww_lang = ww_conf.get("lang")
            if not ww_lang:
                continue
            if include_dialects:
                lang = lang.split("-")[0]
                if ww_lang.startswith(lang):
                    configs[plug] += ww_conf
            elif lang == ww_lang or f"{lang}-{lang}" == ww_lang:
                configs[plug] += ww_conf
    return {k: v for k, v in configs.items() if v}


def get_ww_supported_langs():
    configs = {}
    for plug in find_wake_word_plugins():
        confs = get_ww_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_wake_word_plugin(module_name):
    """Wrapper function for loading wake word plugin.

    Arguments:
        (str) Mycroft wake word module name from config
    """
    return load_plugin(module_name, PluginTypes.WAKEWORD)


class OVOSWakeWordFactory:
    """ replicates the base mycroft class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "dummy": "ovos-ww-plugin-dummy",
        "pocketsphinx": "ovos-ww-plugin-pocketsphinx",
        "precise": "ovos-ww-plugin-precise",
        "snowboy": "ovos-ww-plugin-snowboy",
        "porcupine": "porcupine_wakeword_plug"
    }

    @staticmethod
    def get_class(hotword, config=None):
        config = get_hotwords_config(config)
        if hotword not in config:
            return HotWordEngine
        ww_module = config["module"]
        if ww_module in OVOSWakeWordFactory.MAPPINGS:
            ww_module = OVOSWakeWordFactory.MAPPINGS[ww_module]
        return load_wake_word_plugin(ww_module)

    @staticmethod
    def load_module(module, hotword, config, lang, loop):
        LOG.info(f'Loading "{hotword}" wake word via {module}')
        if module in OVOSWakeWordFactory.MAPPINGS:
            module = OVOSWakeWordFactory.MAPPINGS[module]

        clazz = load_wake_word_plugin(module)
        if clazz is None:
            raise ValueError(f'Wake Word plugin {module} not found')
        LOG.info(f'Loaded the Wake Word plugin {module}')

        return clazz(hotword, config, lang=lang)

    @classmethod
    def create_hotword(cls, hotword="hey mycroft", config=None,
                       lang="en-us", loop=None):
        config = get_hotwords_config(config)
        config = config.get(hotword) or config["hey mycroft"]
        module = config.get("module", "pocketsphinx")
        try:
            return cls.load_module(module, hotword, config, lang, loop)
        except:
            LOG.error(f"failed to created hotword: {config}")
            raise


def get_hotwords_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    return get_plugin_config(config, "hotwords")
