from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes


def find_utterance_transformer_plugins():
    return find_plugins(PluginTypes.UTTERANCE_TRANSFORMER)


def get_utterance_transformer_configs():
    return {plug: get_utterance_transformer_module_configs(plug)
            for plug in find_utterance_transformer_plugins()}


def get_utterance_transformer_module_configs(module_name):
    # utterance plugins return {lang: [list of config dicts]}
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.UTTERANCE_TRANSFORMER) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_utterance_transformer_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_utterance_transformer_plugins():
        configs[plug] = []
        confs = get_utterance_transformer_module_configs(plug)
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


def get_utterance_transformer_supported_langs():
    configs = {}
    for plug in find_utterance_transformer_plugins():
        confs = get_utterance_transformer_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_utterance_transformer_plugin(module_name):
    """Wrapper function for loading text_transformer plugin.

    Arguments:
        (str) Mycroft text_transformer module name from config
    Returns:
        class: found text_transformer plugin class
    """
    return load_plugin(module_name, PluginTypes.UTTERANCE_TRANSFORMER)


def find_text_transformer_plugins():
    return find_utterance_transformer_plugins()


def load_text_transformer_plugin(module_name):
    return load_utterance_transformer_plugin(module_name)
