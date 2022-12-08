from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.postag import PosTagger


def find_postag_plugins():
    return find_plugins(PluginTypes.POSTAG)


def get_postag_configs():
    return {plug: get_postag_module_configs(plug)
            for plug in find_postag_plugins()}


def get_postag_module_configs(module_name):
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.POSTAG) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_postag_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_postag_plugins():
        configs[plug] = []
        confs = get_postag_module_configs(plug)
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


def get_postag_supported_langs():
    configs = {}
    for plug in find_postag_plugins():
        confs = get_postag_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs



def load_postag_plugin(module_name):
    """Wrapper function for loading postag plugin.

    Arguments:
        module_name (str): postag module name from config
    Returns:
        class: PosTagger plugin class
    """
    return load_plugin(module_name, PluginTypes.POSTAG)


class OVOSPosTaggerFactory:
    """ reads mycroft.conf and returns the globally configured plugin """
    MAPPINGS = {
        # default split at sentence boundaries
        # usually helpful in other plugins and included in base class
        "dummy": "ovos-postag-plugin-dummy"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a PosTagger engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``postag`` section with
        the name of a PosTagger module to be read by this method.

        "postag": {
            "module": <engine_name>
        }
        """
        config = get_postag_config(config)
        postag_module = config.get("module", "ovos-postag-plugin-dummy")
        if postag_module in OVOSPosTaggerFactory.MAPPINGS:
            postag_module = OVOSPosTaggerFactory.MAPPINGS[postag_module]
        return load_postag_plugin(postag_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a PosTagger engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``postag`` section with
        the name of a PosTagger module to be read by this method.

        "postag": {
            "module": <engine_name>
        }
        """
        config = config or get_postag_config()
        plugin = config.get("module") or "ovos-postag-plugin-dummy"
        plugin_config = config.get(plugin) or {}
        try:
            clazz = OVOSPosTaggerFactory.get_class(config)
            return clazz(plugin_config)
        except Exception:
            LOG.error(f'Postag plugin {plugin} could not be loaded!')
            return PosTagger()


def get_postag_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    config = config or Configuration()
    return get_plugin_config(config, "postag")


