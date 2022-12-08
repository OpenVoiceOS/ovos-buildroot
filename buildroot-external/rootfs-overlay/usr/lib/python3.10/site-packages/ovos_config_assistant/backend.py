import json
import os

from ovos_backend_client.identity import IdentityManager
from ovos_config.config import RemoteConf, Configuration
from ovos_config.config import update_mycroft_config
from pywebio.input import actions
from pywebio.input import select
from pywebio.output import popup, put_code
from pywebio.output import put_table, put_markdown, put_image, use_scope

from ovos_config_assistant.pairing import pairing_menu


def backend_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/backend_settings.png', 'rb').read()
        put_image(img)

    cfg = Configuration().get("server", {})

    with use_scope("main_view", clear=True):
        t = cfg.get("backend_type", "?")
        items = [
            ['Backend Type', t],
            ['Identity File', cfg.get("identity_file",
                                      IdentityManager.IDENTITY_FILE)]
        ]

        if t != "offline":
            items += [
                ['Backend Host', cfg.get("url", "127.0.0.1")],
                ['Backend Version', cfg.get("version", "v1")]
            ]

        put_table(items)

        if t != "offline":
            put_markdown(f'### Remote Config:')
            rcfg = RemoteConf()
            put_table([
                ['TTS', rcfg.get("tts", {}).get("module")],
                ['Wake Word',  rcfg.get("listener", {}).get("wake_word")],
                ['Date Format',  rcfg.get("date_format")],
                ['Time Format', rcfg.get("time_format")],
                ['System Units', rcfg.get("system_unit")]
            ])

    buttons = [{'label': 'Manage Identity', 'value': "pairing"},
               {'label': 'Change Backend', 'value': "type"},
               {'label': 'Download Config', 'value': "download"}]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    elif opt == "download":
        rcfg.reload()
        with popup("Remote Config:"):
            put_code(json.dumps(rcfg, indent=4), language="json")
    elif opt == "pairing":
        pairing_menu(back_handler=back_handler)
    elif opt == "type":
        cfg["backend_type"] = select("Choose backend type", ["offline", "selene", "personal"])
        if cfg["backend_type"] == "personal":
            url = "http://0.0.0.0:6712"
            cfg["url"] = url
            cfg["version"] = "v1"
        elif cfg["backend_type"] == "selene":
            url = "https://api.mycroft.ai"
            cfg["url"] = url
            cfg["version"] = "v1"
        elif cfg["backend_type"] == "ovos_api":
            url = "https://api.openvoiceos.com"
            cfg["url"] = url
        elif cfg["backend_type"] == "neon_mq":
            url = "https://api.neon.ai"
            cfg["url"] = url
        elif cfg["backend_type"] == "offline":
            url = "127.0.0.1"
            cfg["url"] = url

        update_mycroft_config({"server": cfg}, bus=Configuration.bus)
        with popup(f"Server set to: {cfg['backend_type']}"):
            put_code(json.dumps(cfg, ensure_ascii=True, indent=2), "json")
        Configuration.reload()

    backend_menu(back_handler=back_handler)
