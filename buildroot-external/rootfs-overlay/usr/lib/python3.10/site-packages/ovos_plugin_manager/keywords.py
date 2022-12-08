from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.keywords import KeywordExtractor


def find_keyword_extract_plugins():
    return find_plugins(PluginTypes.KEYWORD_EXTRACTION)

def get_keyword_extract_configs():
    return {plug: get_keyword_extract_module_configs(plug)
            for plug in find_keyword_extract_plugins()}

def get_keyword_extract_module_configs(module_name):
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.KEYWORD_EXTRACTION) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_keyword_extract_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_keyword_extract_plugins():
        configs[plug] = []
        confs = get_keyword_extract_module_configs(plug)
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


def get_keyword_extract_supported_langs():
    configs = {}
    for plug in find_keyword_extract_plugins():
        confs = get_keyword_extract_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_keyword_extract_plugin(module_name):
    """Wrapper function for loading keyword_extract plugin.

    Arguments:
        module_name (str): keyword_extract module name from config
    Returns:
        class: KeywordExtractor plugin class
    """
    return load_plugin(module_name, PluginTypes.KEYWORD_EXTRACTION)


class OVOSKeywordExtractorFactory:
    """ reads mycroft.conf and returns the globally configured plugin """
    MAPPINGS = {
        # default split at sentence boundaries
        # usually helpful in other plugins and included in base class
        "dummy": "ovos-keyword-plugin-dummy"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a KeywordExtractor engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``keyword_extract`` section with
        the name of a KeywordExtractor module to be read by this method.

        "keyword_extract": {
            "module": <engine_name>
        }
        """
        config = get_keyword_extract_config(config)
        keyword_extract_module = config.get("module", "ovos-keyword-plugin-dummy")
        if keyword_extract_module in OVOSKeywordExtractorFactory.MAPPINGS:
            keyword_extract_module = OVOSKeywordExtractorFactory.MAPPINGS[keyword_extract_module]
        return load_keyword_extract_plugin(keyword_extract_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a KeywordExtractor engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``keyword_extract`` section with
        the name of a KeywordExtractor module to be read by this method.

        "keyword_extract": {
            "module": <engine_name>
        }
        """
        config = config or get_keyword_extract_config()
        plugin = config.get("module") or "ovos-keyword-plugin-dummy"
        plugin_config = config.get(plugin) or {}
        try:
            clazz = OVOSKeywordExtractorFactory.get_class(config)
            return clazz(plugin_config)
        except Exception:
            LOG.error(f'Keyword extraction plugin {plugin} could not be loaded!')
            return KeywordExtractor()


def get_keyword_extract_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    config = config or Configuration()
    return get_plugin_config(config, "keyword_extract")


