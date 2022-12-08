from ovos_plugin_manager.utils.config import get_valid_plugin_configs, sort_plugin_configs
from ovos_utils.log import LOG
from ovos_plugin_manager.templates.tts import TTS, TTSContext, TTSValidator, TextToSpeechCache, ConcatTTS, RemoteTTS
from ovos_plugin_manager.utils import load_plugin, find_plugins, PluginTypes, normalize_lang, PluginConfigTypes


def find_tts_plugins():
    return find_plugins(PluginTypes.TTS)


def load_tts_plugin(module_name):
    """Wrapper function for loading tts plugin.

    Arguments:
        (str) Mycroft tts module name from config
    Returns:
        class: found tts plugin class
    """
    return load_plugin(module_name, PluginTypes.TTS)


def get_tts_configs() -> dict:
    """
    Get a dict of plugin names to valid TTS configuration
    @return: dict plugin name to dict of str lang to list of dict valid configs
    """
    return {plug: get_tts_module_configs(plug)
            for plug in find_tts_plugins()}


def get_tts_module_configs(module_name: str) -> dict:
    """
    Get a dict of lang to list of valid config dicts for a specific plugin
    @param module_name: name of plugin to get configurations for
    @return: {lang: [list of config dicts]}
    """
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.TTS) or {}
    configs = {normalize_lang(lang): v for lang, v in cfgs.items()}
    # let's sort by priority key
    for k, v in configs.items():
        configs[k] = sorted(v, key=lambda c: c.get("priority", 60))
    return configs


def get_tts_lang_configs(lang, include_dialects=False):
    """
    Get a dict of plugins names to sorted list of valid configurations
    @param lang: language to get configurations for (i.e. en, en-US)
    @param include_dialects: If true, include configs for other locales
        (i.e. include en-GB configs for lang=en-US)
    @return: dict plugin name to list of valid configs sorted by priority
    """
    lang = normalize_lang(lang)
    matched_configs = {}
    for plug in find_tts_plugins():
        matched_configs[plug] = []
        confs = get_tts_module_configs(plug)
        matched_configs[plug] = get_valid_plugin_configs(confs, lang,
                                                         include_dialects)
    return sort_plugin_configs(matched_configs)


def get_tts_supported_langs():
    """
    Get a dict of languages to valid configuration options
    @return: dict lang to list of plugins that support that lang
    """
    configs = {}
    for plug in find_tts_plugins():
        confs = get_tts_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


class OVOSTTSFactory:
    """ replicates the base mycroft class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "dummy": "ovos-tts-plugin-dummy",
        "mimic": "ovos-tts-plugin-mimic",
        "mimic2": "ovos-tts-plugin-mimic2",
        "mimic3": "ovos-tts-plugin-mimic3",
        "google": "ovos-tts-plugin-google-tx",
        "marytts": "ovos-tts-plugin-marytts",
        # "fatts": FATTS,
        # "festival": Festival,
        "espeak": "ovos_tts_plugin_espeakng",
        # "spdsay": SpdSay,
        # "watson": WatsonTTS,
        # "bing": BingTTS,
        "responsive_voice": "ovos-tts-plugin-responsivevoice",
        # "yandex": YandexTTS,
        "polly": "ovos-tts-plugin-polly",
        # "mozilla": MozillaTTS,
        "pico": "ovos-tts-plugin-pico"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a TTS engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``tts`` section with
        the name of a TTS module to be read by this method.

        "tts": {
            "module": <engine_name>
        }
        """
        config = config or get_tts_config()
        tts_module = config.get("module") or "dummy"
        if tts_module in OVOSTTSFactory.MAPPINGS:
            tts_module = OVOSTTSFactory.MAPPINGS[tts_module]
        return load_tts_plugin(tts_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a TTS engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``tts`` section with
        the name of a TTS module to be read by this method.

        "tts": {
            "module": <engine_name>
        }
        """
        tts_config = get_tts_config(config)
        tts_lang = tts_config["lang"]
        tts_module = tts_config.get('module', 'dummy')
        try:
            clazz = OVOSTTSFactory.get_class(tts_config)
            if clazz:
                LOG.info(f'Found plugin {tts_module}')
                tts = clazz(tts_lang, tts_config)
                tts.validator.validate()
                LOG.info(f'Loaded plugin {tts_module}')
            else:
                raise FileNotFoundError("unknown plugin")
        except Exception:
            LOG.exception('The selected TTS plugin could not be loaded.')
            raise
        return tts


def get_tts_config(config=None):
    from ovos_plugin_manager.utils.config import get_plugin_config
    return get_plugin_config(config)


if __name__ == "__main__":
    configs = get_tts_module_configs('ovos-tts-plugin-mimic2')
    print(configs["en-US"])
    # {'de': [{'display_name': 'Dfki Pavoque Styles',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'dfki-pavoque-styles'},
    #         {'display_name': 'Dfki Pavoque Neutral Hsmm',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'dfki-pavoque-neutral-hsmm'},
    #         {'display_name': 'Dfki Pavoque Neutral',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'dfki-pavoque-neutral'},
    #         {'display_name': 'Bits4',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'bits4'},
    #         {'display_name': 'Bits3 Hsmm',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'bits3-hsmm'},
    #         {'display_name': 'Bits3',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'bits3'},
    #         {'display_name': 'Bits2',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'bits2'},
    #         {'display_name': 'Bits1 Hsmm',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'bits1-hsmm'},
    #         {'display_name': 'Bits1',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'bits1'}],
    #  'en-GB': [{'display_name': 'Dfki Spike Hsmm',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-spike-hsmm'},
    #            {'display_name': 'Dfki Spike',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-spike'},
    #            {'display_name': 'Dfki Prudence Hsmm',
    #             'gender': 'female',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-prudence-hsmm'},
    #            {'display_name': 'Dfki Prudence',
    #             'gender': 'female',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-prudence'},
    #            {'display_name': 'Dfki Poppy Hsmm',
    #             'gender': 'female',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-poppy-hsmm'},
    #            {'display_name': 'Dfki Poppy',
    #             'gender': 'female',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-poppy'},
    #            {'display_name': 'Dfki Obadiah Hsmm',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-obadiah-hsmm'},
    #            {'display_name': 'Dfki Obadiah',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'dfki-obadiah'}],
    #  'en-US': [{'display_name': 'Cmu Slt Hsmm',
    #             'gender': 'female',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'cmu-slt-hsmm'},
    #            {'display_name': 'Cmu Slt',
    #             'gender': 'female',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'cmu-slt'},
    #            {'display_name': 'Cmu Rms Hsmm',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'cmu-rms-hsmm'},
    #            {'display_name': 'Cmu Rms',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'cmu-rms'},
    #            {'display_name': 'Cmu Bdl Hsmm',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'cmu-bdl-hsmm'},
    #            {'display_name': 'Cmu Bdl',
    #             'gender': 'male',
    #             'url': 'http://mary.dfki.de:59125',
    #             'voice': 'cmu-bdl'}],
    #  'fr': [{'display_name': 'Upmc Pierre Hsmm',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'upmc-pierre-hsmm'},
    #         {'display_name': 'Upmc Pierre',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'upmc-pierre'},
    #         {'display_name': 'Upmc Jessica Hsmm',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'upmc-jessica-hsmm'},
    #         {'display_name': 'Upmc Jessica',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'upmc-jessica'},
    #         {'display_name': 'Enst Dennys Hsmm',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'enst-dennys-hsmm'},
    #         {'display_name': 'Enst Camille Hsmm',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'enst-camille-hsmm'},
    #         {'display_name': 'Enst Camille',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'enst-camille'}],
    #  'it': [{'display_name': 'Istc Lucia Hsmm',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'istc-lucia-hsmm'}],
    #  'lb': [{'display_name': 'Marylux',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'marylux'}],
    #  'te': [{'display_name': 'Cmu Nk Hsmm',
    #          'gender': 'female',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'cmu-nk-hsmm'}],
    #  'tr': [{'display_name': 'Dfki Ot Hsmm',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'dfki-ot-hsmm'},
    #         {'display_name': 'Dfki Ot',
    #          'gender': 'male',
    #          'url': 'http://mary.dfki.de:59125',
    #          'voice': 'dfki-ot'}]}

    supported_langs = get_tts_supported_langs()
    # {'af': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'af-ZA': ['ovos-tts-plugin-mimic3'],
    #  'am': ['ovos-tts-plugin-espeakng'],
    #  'an': ['ovos-tts-plugin-espeakng'],
    #  'ar': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'as': ['ovos-tts-plugin-espeakng'],
    #  'az': ['ovos-tts-plugin-espeakng'],
    #  'ba': ['ovos-tts-plugin-espeakng'],
    #  'be': ['ovos-tts-plugin-espeakng'],
    #  'bg': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'bn': ['ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-mimic3'],
    #  'bs': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ca': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'chr': ['ovos-tts-plugin-espeakng'],
    #  'cs': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'cv': ['ovos-tts-plugin-espeakng'],
    #  'cy': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'da': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'de': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-marytts',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-pico',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'el': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'el-GR': ['ovos-tts-plugin-mimic3'],
    #  'en': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-SAM',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-pico'],
    #  'en-GB': ['ovos-tts-plugin-marytts',
    #            'ovos-tts-plugin-espeakng',
    #            'ovos-tts-plugin-mimic3',
    #            'ovos-tts-plugin-mimic'],
    #  'en-US': ['ovos-tts-plugin-marytts',
    #            'ovos-tts-plugin-espeakng',
    #            'neon-tts-plugin-larynx-server',
    #            'ovos-tts-plugin-mimic3',
    #            'ovos-tts-plugin-mimic',
    #            'ovos-tts-plugin-mimic2'],
    #  'eo': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'es': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-pico',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'et': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'eu': ['ovos-tts-plugin-espeakng'],
    #  'fa': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-mimic3'],
    #  'fi': ['ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-mimic3'],
    #  'fil': ['ovos-tts-plugin-google-tx'],
    #  'fr': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-marytts',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-pico',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'fr-BE': ['ovos-tts-plugin-espeakng'],
    #  'fr-CH': ['ovos-tts-plugin-espeakng'],
    #  'ga': ['ovos-tts-plugin-espeakng'],
    #  'gd': ['ovos-tts-plugin-espeakng'],
    #  'gn': ['ovos-tts-plugin-espeakng'],
    #  'gu': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'gu-IN': ['ovos-tts-plugin-mimic3'],
    #  'ha-NE': ['ovos-tts-plugin-mimic3'],
    #  'he': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'hi': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'hr': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ht': ['ovos-tts-plugin-espeakng'],
    #  'hu': ['ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-mimic3'],
    #  'hy': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ia': ['ovos-tts-plugin-espeakng'],
    #  'id': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'io': ['ovos-tts-plugin-espeakng'],
    #  'is': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'it': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-marytts',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-pico',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'ja': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'jv': ['ovos-tts-plugin-google-tx'],
    #  'jv-ID': ['ovos-tts-plugin-mimic3'],
    #  'ka': ['ovos-tts-plugin-espeakng'],
    #  'kk': ['ovos-tts-plugin-espeakng'],
    #  'kl': ['ovos-tts-plugin-espeakng'],
    #  'km': ['ovos-tts-plugin-google-tx'],
    #  'kn': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ko': ['ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-mimic3'],
    #  'ku': ['ovos-tts-plugin-espeakng'],
    #  'ky': ['ovos-tts-plugin-espeakng'],
    #  'la': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'lb': ['ovos-tts-plugin-marytts', 'ovos-tts-plugin-espeakng'],
    #  'lt': ['ovos-tts-plugin-espeakng'],
    #  'lv': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'mi': ['ovos-tts-plugin-espeakng'],
    #  'mk': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ml': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'mr': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ms': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'mt': ['ovos-tts-plugin-espeakng'],
    #  'my': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'nb': ['ovos-tts-plugin-espeakng'],
    #  'ne': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ne-NP': ['ovos-tts-plugin-mimic3'],
    #  'nl': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'no': ['ovos-tts-plugin-google-tx'],
    #  'om': ['ovos-tts-plugin-espeakng'],
    #  'or': ['ovos-tts-plugin-espeakng'],
    #  'pa': ['ovos-tts-plugin-espeakng'],
    #  'piqd': ['ovos-tts-plugin-espeakng'],
    #  'pl': ['ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-mimic3'],
    #  'pt': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx'],
    #  'pt-BR': ['ovos-tts-plugin-espeakng'],
    #  'py': ['ovos-tts-plugin-espeakng'],
    #  'qu': ['ovos-tts-plugin-espeakng'],
    #  'ro': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'ru': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'ru-LV': ['ovos-tts-plugin-espeakng'],
    #  'sd': ['ovos-tts-plugin-espeakng'],
    #  'si': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'sk': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'sl': ['ovos-tts-plugin-espeakng'],
    #  'sq': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'sr': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'su': ['ovos-tts-plugin-google-tx'],
    #  'sv': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'sw': ['ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'neon-tts-plugin-larynx-server',
    #         'ovos-tts-plugin-mimic3'],
    #  'ta': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'te': ['ovos-tts-plugin-marytts',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx'],
    #  'te-IN': ['ovos-tts-plugin-mimic3'],
    #  'th': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'tk': ['ovos-tts-plugin-espeakng'],
    #  'tn': ['ovos-tts-plugin-espeakng'],
    #  'tn-ZA': ['ovos-tts-plugin-mimic3'],
    #  'tr': ['ovos-tts-plugin-marytts',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx'],
    #  'tt': ['ovos-tts-plugin-espeakng'],
    #  'ug': ['ovos-tts-plugin-espeakng'],
    #  'uk': ['ovos-tts-plugin-beepspeak',
    #         'ovos-tts-plugin-espeakng',
    #         'ovos-tts-plugin-google-tx',
    #         'ovos-tts-plugin-mimic3'],
    #  'ur': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'uz': ['ovos-tts-plugin-espeakng'],
    #  'vi': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'vi-VN': ['ovos-tts-plugin-mimic3'],
    #  'yo': ['ovos-tts-plugin-mimic3'],
    #  'zh': ['ovos-tts-plugin-espeakng', 'ovos-tts-plugin-google-tx'],
    #  'zh-CN': ['ovos-tts-plugin-google-tx'],
    #  'zh-TW': ['ovos-tts-plugin-google-tx']}

    lang_configs = get_tts_lang_configs("fr")
    print(lang_configs)
    # {'neon-tts-plugin-larynx-server': [{'display_name': 'gilles le blanc',
    #                                     'gender': '',
    #                                     'voice': 'fr-fr/gilles_le_blanc-glow_tts'},
    #                                    {'display_name': 'siwis',
    #                                     'gender': '',
    #                                     'voice': 'fr_fr/siwis-glow_tts'},
    #                                    {'display_name': 'tom',
    #                                     'gender': '',
    #                                     'voice': 'fr_fr/tom-glow_tts'}],
    #  'ovos-tts-plugin-espeakng': [{'display_name': 'French (France) Male',
    #                                'gender': 'male',
    #                                'lang': 'fr-fr',
    #                                'voice': 'm1'},
    #                               {'display_name': 'French (France) Female',
    #                                'gender': 'female',
    #                                'lang': 'fr-fr',
    #                                'voice': 'f1'}],
    #  'ovos-tts-plugin-google-tx': [{'display_name': 'Google Translate (fr)',
    #                                 'gender': '',
    #                                 'lang': 'fr',
    #                                 'voice': 'default'}],
    #  'ovos-tts-plugin-marytts': [{'display_name': 'Upmc Pierre Hsmm',
    #                               'gender': 'male',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'upmc-pierre-hsmm'},
    #                              {'display_name': 'Upmc Pierre',
    #                               'gender': 'male',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'upmc-pierre'},
    #                              {'display_name': 'Upmc Jessica Hsmm',
    #                               'gender': 'female',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'upmc-jessica-hsmm'},
    #                              {'display_name': 'Upmc Jessica',
    #                               'gender': 'female',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'upmc-jessica'},
    #                              {'display_name': 'Enst Dennys Hsmm',
    #                               'gender': 'male',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'enst-dennys-hsmm'},
    #                              {'display_name': 'Enst Camille Hsmm',
    #                               'gender': 'female',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'enst-camille-hsmm'},
    #                              {'display_name': 'Enst Camille',
    #                               'gender': 'female',
    #                               'url': 'http://mary.dfki.de:59125',
    #                               'voice': 'enst-camille'}],
    #  'ovos-tts-plugin-mimic3': [{'display_name': 'M-Ailabs - Ezwa',
    #                              'gender': '',
    #                              'speaker': 'ezwa',
    #                              'voice': 'fr_FR/m-ailabs_low'},
    #                             {'display_name': 'M-Ailabs - Nadine Eckert Boulet',
    #                              'gender': '',
    #                              'speaker': 'nadine_eckert_boulet',
    #                              'voice': 'fr_FR/m-ailabs_low'},
    #                             {'display_name': 'M-Ailabs - Bernard',
    #                              'gender': '',
    #                              'speaker': 'bernard',
    #                              'voice': 'fr_FR/m-ailabs_low'},
    #                             {'display_name': 'M-Ailabs - Zeckou',
    #                              'gender': '',
    #                              'speaker': 'zeckou',
    #                              'voice': 'fr_FR/m-ailabs_low'},
    #                             {'display_name': 'M-Ailabs - Gilles G Le Blanc',
    #                              'gender': '',
    #                              'speaker': 'gilles_g_le_blanc',
    #                              'voice': 'fr_FR/m-ailabs_low'},
    #                             {'display_name': 'Siwis',
    #                              'gender': '',
    #                              'speaker': 'default',
    #                              'voice': 'fr_FR/siwis_low'},
    #                             {'display_name': 'Tom',
    #                              'gender': '',
    #                              'speaker': 'default',
    #                              'voice': 'fr_FR/tom_low'}],
    #  'ovos-tts-plugin-pico': [{'display_name': 'Pico (fr)',
    #                            'gender': 'female',
    #                            'lang': 'fr',
    #                            'voice': 'default'}]}
