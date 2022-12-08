import json
from typing import Optional

from ovos_utils import flatten_list
from ovos_utils.log import LOG
from ovos_plugin_manager import PluginTypes
from ovos_plugin_manager.stt import get_stt_lang_configs
from ovos_plugin_manager.tts import get_tts_lang_configs


def hash_dict(d):
    return str(hash(json.dumps(d, indent=2, sort_keys=True,
                               ensure_ascii=True)))


class PluginUIHelper:
    """
    Helper class to provide metadata for UI consumption
    This allows all sorts of rich integrations by
    any downstream application wanting to provide a plugin store

    This is the central place to manage anything UI related,
    downstream should not need to import anything else
    """
    _stt_opts = {}
    _tts_opts = {}
    _stt_init = False
    _tts_init = False

    @classmethod
    def config2option(cls, cfg: dict, plugin_type: PluginTypes,
                      lang: str = None) -> dict:
        """
        Get the equivalent UI display model from a plugin config.
        This is the inverse of option2config.
        @param cfg: Configuration from plugin entrypoint
        @param plugin_type: Plugin type (stt/tts)
        @param lang: ISO 639-1 or BCP-47 language requested
        @return: GUI-compatible plugin spec
        """
        cfg = cls._migrate_old_cfg(cfg)
        engine = cfg["module"]
        lang = lang or cfg.get("lang")

        plugin_display_name = engine.replace("_", " ").replace("-",
                                                               " ").title()
        display_name = cfg["meta"].get("display_name", "?")
        # TODO consider better handling of missing "offline" key
        offline = cfg["meta"].get("offline", False)

        opt = {"plugin_name": plugin_display_name,  # Name of the plugin
               "display_name": display_name,  # Name of this config option
               "offline": offline,
               "lang": lang,
               "engine": engine,
               "plugin_type": plugin_type}

        # Init class dict config options for all plugins of this type
        if plugin_type == PluginTypes.STT:
            if lang and not cls._stt_init:
                LOG.warning("requested STT options before call to "
                            "`get_config_options`")
                # do initial scan
                cls.get_config_options(lang, PluginTypes.STT)
            cls._stt_opts[hash_dict(opt)] = cfg
        elif plugin_type == PluginTypes.TTS:
            if lang and not cls._tts_init:
                LOG.warning("requested TTS options before call to "
                            "`get_config_options`")
                # do initial scan
                cls.get_config_options(lang, PluginTypes.TTS)
            opt["gender"] = cfg["meta"].get("gender", "?")
            cls._tts_opts[hash_dict(opt)] = cfg
        else:
            raise NotImplementedError(
                "only STT and TTS plugins are supported at this time")
        return opt

    @classmethod
    def option2config(cls, opt: dict, plugin_type: PluginTypes = None) -> dict:
        """
        Get the equivalent plugin config from a UI display model.
        This is the inverse of config2option.
        @param opt: Configuration from GUI
        @param plugin_type: Plugin type (stt/tts)
        @return: plugin configuration for requested opt (lang, meta, module)
        """
        plugin_type = plugin_type or opt.get("plugin_type")
        if not plugin_type:
            raise ValueError("Unknown plugin type")
        if plugin_type == PluginTypes.STT:
            cfg = cls._stt_opts.get(hash_dict(opt)) or dict()
        elif plugin_type == PluginTypes.TTS:
            cfg = cls._tts_opts.get(hash_dict(opt)) or dict()
        else:
            raise NotImplementedError(
                "only STT and TTS plugins are supported at this time")
        LOG.debug(f'cfg={cfg}')
        return cfg

    @staticmethod
    def _migrate_old_cfg(cfg: dict) -> dict:
        """
        Translate any old-style plugin configuration into new structure
        @param cfg: Plugin config to check
        @return: Validated plugin config
        """
        if cfg.get('meta'):
            return cfg
        LOG.info(f"Migrating old-style configuration: {cfg}")
        meta = {}
        for k in ["display_name", "gender", "offline", "priority"]:
            if k in cfg:
                meta[k] = cfg.pop(k)
        cfg["meta"] = meta
        LOG.debug(f"Config migrated to: {cfg}")
        return cfg

    @classmethod
    def get_config_options(cls, lang: str, plugin_type: PluginTypes,
                           blacklist: Optional[list] = None,
                           preferred: Optional[list] = None,
                           max_opts: int = 50, skip_setup: bool = True,
                           include_dialects: bool = True) -> list:
        """
        Get a list of dict metadata for downstream UIs.
        Each option corresponds to a valid selectable plugin configuration;
        each plugin may report several options.
        @param lang: Requested language (ISO 639-1 or BCP-47)
        @param plugin_type: Type of plugins to return
        @param blacklist: plugin names to ignore
        @param preferred: preferred plugin names to prepend to returned list
        @param max_opts: maximum length of the returned list
        @param skip_setup: If True, exclude any plugins that require setup
        @param include_dialects: If True, include any ISO 639-1 matched codes
        @return: list of valid GUI-compatible config dicts
        """
        # NOTE: mycroft-gui will crash if theres more than 20 options according to @aiix
        # TODO - validate that this is true and 20 is a real limit
        blacklist = blacklist or []
        opts = []
        preferred = preferred or []
        if isinstance(preferred, str):
            preferred = [preferred]
        if plugin_type == PluginTypes.STT:
            cfgs = get_stt_lang_configs(lang=lang, include_dialects=include_dialects)
            cls._stt_init = True
        elif plugin_type == PluginTypes.TTS:
            cfgs = get_tts_lang_configs(lang=lang, include_dialects=include_dialects)
            cls._tts_init = True
        else:
            raise NotImplementedError("only STT and TTS plugins are supported at this time")

        LOG.debug(f"cfgs={cfgs}")
        for engine, configs in cfgs.items():
            if engine in blacklist:
                continue
            pref_opts = []
            for config in configs:
                config = cls._migrate_old_cfg(config)
                if config["meta"].get("extra_setup"):
                    optional = config["meta"]["extra_setup"].get("optional")
                    if not optional and skip_setup:
                        # this config requires additional manual setup, skip was requested
                        LOG.debug(f"Extra setup required. Ignoring {engine}")
                        continue
                config["module"] = engine  # this one should be ensured by get_lang_configs, but just in case
                d = cls.config2option(config, plugin_type, lang)
                if engine in preferred:
                    # Sort the list for UI to display the preferred STT engine first
                    # allow images to set a preferred engine
                    pref_opts.append(d)
                else:
                    opts.append(d)

            # artificially send preferred engine entries to start of list
            opts = pref_opts + opts
        LOG.debug(f"Got {len(opts)} opts")
        return opts[:min(max_opts, len(opts))]

    @classmethod
    def get_plugin_options(cls, lang: str, plugin_type: PluginTypes) -> list:
        """
        Get a list of dict metadata for downstream UIs.
        Each option corresponds to a valid plugin and its capabilities
        @param lang: Requested language (ISO 639-1 or BCP-47)
        @param plugin_type: Type of plugins to return
        @return: list of plugin specs with capabilities and config options
        """
        plugs = {}
        for entry in cls.get_config_options(lang, plugin_type):
            engine = entry["engine"]
            if engine not in plugs:
                plugs[engine] = {"engine": entry["engine"],
                                 "plugin_name": entry["plugin_name"],
                                 "supports_offline_mode": False,
                                 "supports_online_mode": False,
                                 "options": []}
                if plugin_type == PluginTypes.TTS:
                    plugs[engine]["supports_male_voice"] = False
                    plugs[engine]["supports_female_voice"] = False

            if "offline" in entry:
                if entry["offline"]:
                    plugs[engine]["supports_offline_mode"] = True
                else:
                    plugs[engine]["supports_online_mode"] = True

            if entry.get("gender", "?") == "male":
                plugs[engine]["supports_male_voice"] = True
            elif entry.get("gender", "?") == "female":
                plugs[engine]["supports_female_voice"] = True

            plugs[engine]["options"].append(entry)

        opts = flatten_list(list(plugs.values()))
        LOG.debug(opts)
        return opts

    @classmethod
    def get_extra_setup(cls, opt: dict,
                        plugin_type: Optional[PluginTypes] = None) -> dict:
        """
        Get a dict representation of plugin configuration options.

        Individual plugins can provide an equivalent structure to skills
        settingsmeta.json/yaml.
        This can be used to display an extra step for plugin configuration,
        such as required api keys that cant be pre-included by plugins.

        Skills already define this data structure that allows exposing
        arbitrary configurations to downstream UIs,
        with selene being the reference consumer of that API.
        @param opt: Configuration from GUI
        @param plugin_type: Plugin type (stt/tts)
        @return: dict `extra_setup` from plugin 'meta' config
        """
        plugin_type = plugin_type or opt.get("plugin_type")
        if not plugin_type:
            raise ValueError("Unknown plugin type")
        meta = cls.option2config(opt, plugin_type).get("meta")
        if not meta:
            LOG.warning(f'No meta config found for opt={opt}')
            return {}
        return meta.get("extra_setup") or {}
