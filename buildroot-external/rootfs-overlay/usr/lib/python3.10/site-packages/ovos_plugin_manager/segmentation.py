from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.segmentation import Segmenter


def find_segmentation_plugins():
    return find_plugins(PluginTypes.UTTERANCE_SEGMENTATION)


def get_segmentation_configs():
    return {plug: get_segmentation_module_configs(plug)
            for plug in find_segmentation_plugins()}


def get_segmentation_module_configs(module_name):
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.UTTERANCE_SEGMENTATION) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_segmentation_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_segmentation_plugins():
        configs[plug] = []
        confs = get_segmentation_module_configs(plug)
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


def get_segmentation_supported_langs():
    configs = {}
    for plug in find_segmentation_plugins():
        confs = get_segmentation_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_segmentation_plugin(module_name):
    """Wrapper function for loading segmentation plugin.

    Arguments:
        module_name (str): segmentation module name from config
    Returns:
        class: Segmenter plugin class
    """
    return load_plugin(module_name, PluginTypes.UTTERANCE_SEGMENTATION)


class OVOSUtteranceSegmenterFactory:
    """ reads mycroft.conf and returns the globally configured plugin """
    MAPPINGS = {
        # default split at sentence boundaries
        # usually helpful in other plugins and included in base class
        "dummy": "ovos-segmentation-plugin-quebrafrases"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a Segmenter engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``segmentation`` section with
        the name of a Segmenter module to be read by this method.

        "segmentation": {
            "module": <engine_name>
        }
        """
        config = get_segmentation_config(config)
        segmentation_module = config.get("module", "ovos-segmentation-plugin-quebrafrases")
        if segmentation_module in OVOSUtteranceSegmenterFactory.MAPPINGS:
            segmentation_module = OVOSUtteranceSegmenterFactory.MAPPINGS[segmentation_module]
        return load_segmentation_plugin(segmentation_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a Segmenter engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``segmentation`` section with
        the name of a Segmenter module to be read by this method.

        "segmentation": {
            "module": <engine_name>
        }
        """
        config = config or get_segmentation_config()
        plugin = config.get("module") or "ovos-segmentation-plugin-quebrafrases"
        plugin_config = config.get(plugin) or {}
        try:
            clazz = OVOSUtteranceSegmenterFactory.get_class(config)
            return clazz(plugin_config)
        except Exception:
            LOG.error(f'Utterance Segmentation plugin {plugin} could not be loaded!')
            return Segmenter()


def get_segmentation_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    config = config or Configuration()
    return get_plugin_config(config, "segmentation")



