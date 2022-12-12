import json
import os

from ovos_config import Configuration
from ovos_config.config import update_mycroft_config
from ovos_plugin_manager.stt import get_stt_configs, get_stt_supported_langs, get_stt_lang_configs
from ovos_plugin_manager.tts import get_tts_configs, get_tts_supported_langs, get_tts_lang_configs
from pywebio.input import select, actions, input_group, input, TEXT, NUMBER
from pywebio.output import put_table, popup, put_code, put_image, use_scope


def _get_stt_opts(lang=None):
    stt_configs = {}
    if lang is not None:
        for p, data in get_stt_lang_configs(lang, include_dialects=True).items():
            if not data:
                continue
            for cfg in data:
                cfg = dict(cfg)
                cfg["module"] = p
                cfg["display_name"] = f"{cfg['display_name']} [{p}]"
                stt_configs[cfg["display_name"]] = cfg
    else:
        for p, data in get_stt_configs().items():
            if not data:
                continue
            for lang, confs in data.items():
                for cfg in confs:
                    cfg = dict(cfg)
                    cfg["module"] = p
                    cfg["display_name"] = f"{cfg['display_name']} [{p}]"
                    stt_configs[cfg["display_name"]] = cfg
    return stt_configs


def _get_tts_opts(lang=None):
    tts_configs = {}
    if lang is not None:
        for p, data in get_tts_lang_configs(lang, include_dialects=True).items():
            if not data:
                continue
            for cfg in data:
                cfg = dict(cfg)
                cfg["module"] = p
                if f" [{p}]" not in cfg['display_name']:
                    cfg["display_name"] = f"{cfg['display_name']} [{p}]"
                tts_configs[cfg["display_name"]] = cfg
    else:
        for p, data in get_tts_configs().items():
            if not data:
                continue
            for lang, confs in data.items():
                for cfg in confs:
                    cfg = dict(cfg)
                    cfg["module"] = p
                    if f" [{p}]" not in cfg['display_name']:
                        cfg["display_name"] = f"{cfg['display_name']} [{p}]"
                    tts_configs[cfg["display_name"]] = cfg
    return tts_configs


def plugins_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/plugins_manager.png', 'rb').read()
        put_image(img)

    cfg = Configuration()
    print(cfg.get("hotwords"))
    stt_config = cfg["stt"]
    tts_config = cfg["tts"]

    with use_scope("main_view", clear=True):
        put_table([
            ['Module', "Plugin"],
            ['STT', stt_config["module"]],
            ['Fallback STT', stt_config["fallback_module"]],
            ['TTS', tts_config["module"]],
            ['Fallback TTS', tts_config["fallback_module"]]
        ])

    buttons = [{'label': 'Change STT', 'value': "stt"},
               {'label': 'Change TTS', 'value': "tts"},
               {'label': 'Change Fallback STT', 'value': "fallback_stt"},
               {'label': 'Change Fallback TTS', 'value': "fallback_tts"}
               ]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    elif opt == "stt":
        lang = Configuration().get("lang")
        lang = lang or select("Choose STT default language",
                              list(get_stt_supported_langs().keys()))
        cfgs = _get_stt_opts(lang)
        stt = select("Choose a speech to text engine", list(cfgs.keys()))
        m = cfgs[stt].pop("module")
        stt_config["module"] = m
        stt_config[m] = cfgs[stt]
        update_mycroft_config({"stt": stt_config}, bus=cfg.bus)
        with popup(f"STT set to: {stt}"):
            put_code(json.dumps(stt_config, ensure_ascii=True, indent=2), "json")
    elif opt == "tts":
        lang = Configuration().get("lang")
        lang = lang or select("Choose TTS default language",
                              list(get_tts_supported_langs().keys()))
        cfgs = _get_tts_opts(lang)
        tts = select("Choose a text to speech engine", list(cfgs.keys()))
        m = cfgs[tts].pop("module")
        tts_config["module"] = m
        tts_config[m] = cfgs[tts]
        update_mycroft_config({"tts": tts_config}, bus=cfg.bus)
        with popup(f"TTS set to: {tts}"):
            put_code(json.dumps(tts_config, ensure_ascii=True, indent=2), "json")
    elif opt == "fallback_stt":
        lang = Configuration().get("lang")
        lang = lang or select("Choose STT default language",
                              list(get_stt_supported_langs().keys()))
        cfgs = _get_stt_opts(lang)
        stt = select("Choose a fallback speech to text engine", list(cfgs.keys()))
        m = cfgs[stt].pop("module")
        stt_config["fallback_module"] = m
        stt_config[m] = cfgs[stt]
        update_mycroft_config({"stt": stt_config}, bus=cfg.bus)
        with popup(f"Fallback STT set to: {stt}"):
            put_code(json.dumps(stt_config, ensure_ascii=True, indent=2), "json")
    elif opt == "fallback_tts":
        lang = Configuration().get("lang")
        lang = lang or select("Choose Fallback TTS default language",
                              list(get_tts_supported_langs().keys()))
        cfgs = _get_tts_opts(lang)
        tts = select("Choose a fallback text to speech engine", list(cfgs.keys()))
        m = cfgs[tts].pop("module")
        tts_config["fallback_module"] = m
        tts_config[m] = cfgs[tts]
        update_mycroft_config({"tts": tts_config}, bus=cfg.bus)
        with popup(f"Fallback TTS set to: {tts}"):
            put_code(json.dumps(tts_config, ensure_ascii=True, indent=2), "json")

    cfg.reload()  # ensure changes reflected
    plugins_menu(back_handler=back_handler)
