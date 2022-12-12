from ovos_plugin_manager.utils import normalize_lang, load_plugin, find_plugins, PluginTypes, PluginConfigTypes


def find_metadata_transformer_plugins():
    return find_plugins(PluginTypes.METADATA_TRANSFORMER)


def get_metadata_transformer_configs():
    return {plug: get_metadata_transformer_module_configs(plug)
            for plug in find_metadata_transformer_plugins()}


def get_metadata_transformer_module_configs(module_name):
    cfgs = load_plugin(module_name + ".config", PluginConfigTypes.METADATA_TRANSFORMER) or {}
    return {normalize_lang(lang): v for lang, v in cfgs.items()}


def get_metadata_transformer_lang_configs(lang, include_dialects=False):
    lang = normalize_lang(lang)
    configs = {}
    for plug in find_metadata_transformer_plugins():
        configs[plug] = []
        confs = get_metadata_transformer_module_configs(plug)
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


def get_metadata_transformer_supported_langs():
    configs = {}
    for plug in find_metadata_transformer_plugins():
        confs = get_metadata_transformer_module_configs(plug)
        for lang, cfgs in confs.items():
            if confs:
                if lang not in configs:
                    configs[lang] = []
                configs[lang].append(plug)
    return configs


def load_metadata_transformer_plugin(module_name):
    """Wrapper function for loading metadata_transformer plugin.

    Arguments:
        (str) Mycroft metadata_transformer module name from config
    Returns:
        class: found metadata_transformer plugin class
    """
    return load_plugin(module_name, PluginTypes.METADATA_TRANSFORMER)