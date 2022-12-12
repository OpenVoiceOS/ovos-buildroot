import json
import os

from ovos_config import Configuration
from ovos_config.config import update_mycroft_config
from pywebio.input import select, actions, input_group, input, TEXT, NUMBER
from pywebio.output import put_table, popup, put_code, put_image, use_scope


def microservices_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/microservices_config.png', 'rb').read()
        put_image(img)

    cfg = Configuration()
    api_cfg = cfg.get("microservices") or {}
    backend_cfg = cfg["server"]

    with use_scope("main_view", clear=True):
        put_table([
            ['Default provider', backend_cfg.get("backend_type", "offline")],
            ['WolframAlpha provider', api_cfg.get("wolfram_provider", "auto")],
            ['Weather provider', api_cfg.get("weather_provider", "auto")],
            ['Geolocation provider', api_cfg.get("geolocation_provider", "auto")],
            ['Email provider', api_cfg.get("email_provider", "auto")],
        ])

    buttons = [{'label': 'Configure Secrets', 'value': "secrets"},
               {'label': 'Configure SMTP', 'value': "smtp"},
               {'label': 'Configure Wolfram Alpha', 'value': "wolfram"},
               {'label': 'Configure Weather', 'value': "weather"},
               {'label': 'Configure Geolocation', 'value': "geo"},
               {'label': 'Configure Email', 'value': "email"}]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    elif opt == "email":
        opts = ["NeonMQ"]
        if api_cfg["email"]["smtp"].get("password"):
            opts.insert(0, "SMTP")
        if backend_cfg.get("backend_type", "") == "selene":
            opts.append("Selene")
        provider = select("Choose a email provider", opts)
        if provider == "SMTP":
            api_cfg["email_provider"] = "smtp"
        if provider == "Selene":
            api_cfg["email_provider"] = "selene"
        if provider == "NeonMQ":
            api_cfg["email_provider"] = "neon"
        update_mycroft_config({"microservices": api_cfg}, bus=cfg.bus)
    elif opt == "geo":
        opts = ["OpenStreetMap", "OpenVoiceOS", "NeonMQ"]
        if backend_cfg.get("backend_type", "") == "selene":
            opts.append("Selene")
        provider = select("Choose a geolocation provider", opts)
        if provider == "OpenStreetMap":
            api_cfg["geolocation_provider"] = "osm"
        if provider == "Selene":
            api_cfg["geolocation_provider"] = "selene"
        if provider == "OpenVoiceOS":
            api_cfg["geolocation_provider"] = "ovos"
        if provider == "NeonMQ":
            api_cfg["geolocation_provider"] = "neon"
        update_mycroft_config({"microservices": api_cfg}, bus=cfg.bus)
    elif opt == "weather":
        opts = ["OpenVoiceOS", "NeonMQ"]
        if api_cfg.get("owm_key"):
            opts.append("OpenWeatherMap")
        if backend_cfg.get("backend_type", "") == "selene":
            opts.append("Selene")
        provider = select("Choose a weather provider", opts)
        if provider == "OpenWeatherMap":
            api_cfg["weather_provider"] = "owm"
        if provider == "Selene":
            api_cfg["weather_provider"] = "selene"
        if provider == "OpenVoiceOS":
            api_cfg["weather_provider"] = "ovos"
        if provider == "NeonMQ":
            api_cfg["weather_provider"] = "neon"
        update_mycroft_config({"microservices": api_cfg}, bus=cfg.bus)
    elif opt == "wolfram":
        opts = ["OpenVoiceOS", "NeonMQ"]
        if api_cfg.get("wolfram_key"):
            opts.append("WolframAlpha")
        if backend_cfg.get("backend_type", "") == "selene":
            opts.append("Selene")
        provider = select("Choose a WolframAlpha provider", opts)
        if provider == "WolframAlpha":
            api_cfg["wolfram_provider"] = "wolfram"
        if provider == "Selene":
            api_cfg["wolfram_provider"] = "selene"
        if provider == "OpenVoiceOS":
            api_cfg["wolfram_provider"] = "ovos"
        if provider == "NeonMQ":
            api_cfg["wolfram_provider"] = "neon"
        update_mycroft_config({"microservices": api_cfg}, bus=cfg.bus)
    elif opt == "secrets":
        data = input_group('Secret Keys', [
            input("WolframAlpha key", value="TODO",
                  type=TEXT, name='wolfram'),
            input("OpenWeatherMap key", value="TODO",
                  type=TEXT, name='owm')
        ])
        api_cfg["wolfram_key"] = data["wolfram"]
        api_cfg["own_key"] = data["owm"]
        update_mycroft_config({"microservices": api_cfg}, bus=cfg.bus)
        popup("Secrets updated!")
    elif opt == "smtp":
        if "email" not in api_cfg:
            api_cfg["email"] = {}
        if "smtp" not in api_cfg["email"]:
            api_cfg["email"]["smtp"] = {}

        data = input_group('SMTP Configuration', [
            input("Username", value=api_cfg["email"]["smtp"].get("username", 'user'),
                  type=TEXT, name='username'),
            input("Password", value=api_cfg["email"]["smtp"].get("password", '***********'),
                  type=TEXT, name='password'),
            input("Host", value=api_cfg["email"]["smtp"].get("host", 'smtp.mailprovider.com'),
                  type=TEXT, name='host'),
            input("Port", value=api_cfg["email"]["smtp"].get("port", '465'),
                  type=NUMBER, name='port')
        ])

        api_cfg["email"]["smtp"]["username"] = data["username"]
        api_cfg["email"]["smtp"]["password"] = data["password"]
        api_cfg["email"]["smtp"]["host"] = data["host"]
        api_cfg["email"]["smtp"]["port"] = data["port"]
        with popup(f"SMTP configuration for: {data['host']}"):
            put_code(json.dumps(data, ensure_ascii=True, indent=2), "json")

        update_mycroft_config({"microservices": api_cfg}, bus=cfg.bus)

    cfg.reload()  # ensure changes reflected
    microservices_menu(back_handler=back_handler)
