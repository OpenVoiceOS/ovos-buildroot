from typing import Optional
from ovos_config.config import Configuration
from ovos_utils.log import LOG


def get_plugin_config(config: Optional[dict] = None, section: str = None,
                      module: Optional[str] = None) -> dict:
    """
    Get a configuration dict for the specified plugin
    @param config: Base configuration to parse, defaults to `Configuration()`
    @param section: Config section for the plugin (i.e. TTS, STT, language)
    @param module: Module/plugin to get config for, default reads from config
    @return: Configuration for the requested module, including `lang` and `module` keys
    """
    config = config or Configuration()
    lang = config.get('lang') or Configuration().get('lang')
    config = (config.get('intentBox', {}).get(section) or config.get(section)
              or config) if section else config
    module = module or config.get('module')
    if module:
        module_config = config.get(module) or dict()
        module_config.setdefault('lang', lang)
        module_config.setdefault('module', module)
        return module_config
    if section not in ["hotwords", "VAD", "listener"]:
        config.setdefault('lang', lang)
    return config


def get_valid_plugin_configs(configs: dict, lang: str,
                             include_dialects: bool) -> list:
    """
    Get a sorted dict of configurations for a particular plugin
    @param configs: dict of normalized language to sorted list of valid dict
                    configurations for a particular plugin
    @param lang: normalized language to return valid configurations for
    @param include_dialects: if True, include configs for alternate dialects
    @return: list of valid configurations matching the requested lang
    """
    valid_configs = list()
    if include_dialects:
        # Check other dialects of the requested language
        base_lang = lang.split("-")[0]
        for language, confs in configs.items():
            if language.startswith(base_lang):
                for config in confs:
                    try:
                        if language != lang:
                            # Dialect match, boost priority
                            config["priority"] = config.get("priority",
                                                            60) + 15
                        valid_configs.append(config)
                    except Exception as e:
                        LOG.error(f'config={config}')
                        LOG.exception(e)
    elif lang in configs:
        # Exact language/dialog match
        valid_configs.append(configs[lang])
    elif f"{lang}-{lang}" in configs:
        # match (some) default locales
        valid_configs.append(configs[f"{lang}-{lang}"])
    LOG.debug(f'Found {len(valid_configs)} valid configurations for {lang}')
    return valid_configs


def sort_plugin_configs(configs: dict) -> dict:
    """
    Sort a dict of plugin name to valid configurations by priority
    @param configs: dict config name to valid configurations
    @return: dict of sorted lists with highest priority at the end of the list
    """
    bad_plugs = []
    for plug_name, plug_configs in configs.items():
        LOG.debug(plug_configs)
        try:
            configs[plug_name] = sorted(plug_configs,
                                        key=lambda c: c.get("priority", 60))
        except:
            LOG.exception(f"Invalid plugin data: {plug_name}")
            bad_plugs.append(plug_name)

    for plug_name in [p for p in bad_plugs if p in configs]:
        configs.pop(plug_name)

    LOG.debug(configs)
    return {k: v for k, v in configs.items() if v}
