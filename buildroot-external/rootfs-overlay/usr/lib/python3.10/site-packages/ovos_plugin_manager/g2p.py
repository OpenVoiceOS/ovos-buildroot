from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes
from ovos_plugin_manager.templates.g2p import Grapheme2PhonemePlugin, PhonemeAlphabet
from ovos_utils.log import LOG
from ovos_config import Configuration


def find_g2p_plugins():
    return find_plugins(PluginTypes.PHONEME)


def get_g2p_configs():
    return {plug: get_g2p_module_configs(plug)
            for plug in find_g2p_plugins()}


def get_g2p_module_configs(module_name):
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.PHONEME) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_g2p_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_g2p_plugins():
        configs[plug] = []
        confs = get_g2p_module_configs(plug)
        if include_dialects:
            lang = lang.split("-")[0]
            for l in confs:
                if l.startswith(lang):
                    configs[plug] += confs[l]
        elif lang in confs:
            configs[plug] += confs[lang]
        elif f"{lang}-{lang}" in confs:
            configs[plug] += confs[f"{lang}-{lang}"]
    return {k: v for k, v in configs.items() if v}


def get_g2p_supported_langs():
    configs = {}
    for plug in find_g2p_plugins():
        confs = get_g2p_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_g2p_plugin(module_name):
    return load_plugin(module_name, PluginTypes.PHONEME)


class OVOSG2PFactory:
    """ replicates the base mycroft class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "dummy": "ovos-g2p-plugin-dummy",
        "phoneme_guesser": "neon-g2p-plugin-phoneme-guesser",
        "gruut": "neon-g2p-plugin-gruut"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a G2P engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``g2p`` section with
        the name of a G2P module to be read by this method.

        "g2p": {
            "module": <engine_name>
        }
        """
        config = get_g2p_config(config)
        g2p_module = config.get("module") or 'dummy'
        if g2p_module == 'dummy':
            return Grapheme2PhonemePlugin
        if g2p_module in OVOSG2PFactory.MAPPINGS:
            g2p_module = OVOSG2PFactory.MAPPINGS[g2p_module]
        return load_g2p_plugin(g2p_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a G2P engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``g2p`` section with
        the name of a G2P module to be read by this method.

        "g2p": {
            "module": <engine_name>
        }
        """
        g2p_config = get_g2p_config(config)
        g2p_module = g2p_config.get('module', 'dummy')
        try:
            clazz = OVOSG2PFactory.get_class(g2p_config)
            g2p = clazz(g2p_config)
            LOG.debug(f'Loaded plugin {g2p_module}')
        except Exception:
            LOG.exception('The selected G2P plugin could not be loaded.')
            raise
        return g2p


def get_g2p_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    return get_plugin_config(config, "g2p")
