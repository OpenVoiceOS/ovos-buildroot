from ovos_plugin_manager.utils.config import get_plugin_config
from ovos_utils.log import LOG

from ovos_config import Configuration
from ovos_plugin_manager.utils import load_plugin, find_plugins, PluginTypes, PluginConfigTypes


def find_tx_plugins():
    return find_plugins(PluginTypes.TRANSLATE)


def get_tx_configs():
    return {plug: get_tx_module_configs(plug)
            for plug in find_tx_plugins()}


def get_tx_module_configs(module_name):
    return load_plugin(module_name + ".config",
                       PluginConfigTypes.TRANSLATE)


def load_tx_plugin(module_name):
    return load_plugin(module_name, PluginTypes.TRANSLATE)


def find_lang_detect_plugins():
    return find_plugins(PluginTypes.LANG_DETECT)


def get_lang_detect_configs():
    return {plug: get_lang_detect_module_configs(plug)
            for plug in find_lang_detect_plugins()}


def get_lang_detect_module_configs(module_name):
    return load_plugin(module_name + ".config",
                       PluginConfigTypes.LANG_DETECT)


def load_lang_detect_plugin(module_name):
    return load_plugin(module_name, PluginTypes.LANG_DETECT)


class OVOSLangDetectionFactory:
    """ replicates the base neon class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "libretranslate": "libretranslate_detection_plug",
        "google": "googletranslate_detection_plug",
        "amazon": "amazontranslate_detection_plug",
        "cld2": "cld2_plug",
        "cld3": "cld3_plug",
        "langdetect": "langdetect_plug",
        "fastlang": "fastlang_plug",
        "lingua_podre": "lingua_podre_plug"
    }

    # TODO - get_class method

    @staticmethod
    def create(config=None):
        """Factory method to create a LangDetection engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``language`` section with
        the name of a LangDetection module to be read by this method.

         "language": {
            "detection_module": <engine_name>
          }
        """
        try:
            config = config or Configuration()
            if "language" in config:
                config = config["language"]
            lang_module = config.get("detection_module", "libretranslate_detection_plug")
            if lang_module in OVOSLangDetectionFactory.MAPPINGS:
                lang_module = OVOSLangDetectionFactory.MAPPINGS[lang_module]

            clazz = load_lang_detect_plugin(lang_module)
            if clazz is None and lang_module != "libretranslate_detection_plug":
                lang_module = "libretranslate_detection_plug"
                LOG.error(f'Language Translation plugin {lang_module} not found\n'
                          f'Falling back to libretranslate plugin')
                clazz = load_tx_plugin("libretranslate_detection_plug")
            if clazz is None:
                raise ValueError(f'Language Detection plugin {lang_module} not found')
            LOG.info(f'Loaded the Language Detection plugin {lang_module}')
            return clazz(config=get_plugin_config(config, "language", lang_module))
        except Exception:
            # The Language Detection backend failed to start.
            LOG.exception('The selected Language Detection plugin could not be loaded!')
            raise


class OVOSLangTranslationFactory:
    """ replicates the base neon class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "libretranslate": "libretranslate_plug",
        "google": "googletranslate_plug",
        "amazon": "amazontranslate_plug",
        "apertium": "apertium_plug"
    }

    # TODO - get_class method
    @staticmethod
    def create(config=None):
        """Factory method to create a LangTranslation engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``language`` section with
        the name of a LangDetection module to be read by this method.


          "language": {
            "translation_module": <engine_name>
          }
        """
        try:
            config = config or Configuration()
            if "language" in config:
                config = config["language"]
            lang_module = config.get("translation_module", "libretranslate_plug")
            if lang_module in OVOSLangTranslationFactory.MAPPINGS:
                lang_module = OVOSLangTranslationFactory.MAPPINGS[lang_module]
            clazz = load_tx_plugin(lang_module)
            if clazz is None and lang_module != "libretranslate_plug":
                lang_module = "libretranslate_plug"
                LOG.error(f'Language Translation plugin {lang_module} not found\n'
                          f'Falling back to libretranslate plugin')
                clazz = load_tx_plugin("libretranslate_plug")
            if clazz is None:
                raise ValueError(f'Language Translation plugin {lang_module} not found')
            LOG.info(f'Loaded the Language Translation plugin {lang_module}')
            return clazz(config=get_plugin_config(config, "language", lang_module))
        except Exception:
            # The Language Detection backend failed to start.
            LOG.exception('The selected Language Translation plugin could not be loaded!')
            raise
