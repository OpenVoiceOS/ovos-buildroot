import json
import os

from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.utils.geolocate import get_location_config
from pywebio.input import textarea, select, actions
from pywebio.output import put_table, put_markdown, popup, put_code, put_image, use_scope


def backend_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/backend_config.png', 'rb').read()
        put_image(img)

    with use_scope("main_view", clear=True):
        put_table([
            ['Backend Port', CONFIGURATION["backend_port"]],
            ['Device Authentication enabled', not CONFIGURATION["skip_auth"]],
            ['Location override enabled', CONFIGURATION["override_location"]],
            ['IP Geolocation enabled', CONFIGURATION["geolocate"]],
            ['Selene Proxy enabled', CONFIGURATION["selene"]["enabled"]],
            ['Default TTS', CONFIGURATION["default_tts"]],
            ['Default Wake Word', CONFIGURATION["default_ww"]],
            ['Default date format', CONFIGURATION["date_format"]],
            ['Default time format', CONFIGURATION["time_format"]],
            ['Default system units', CONFIGURATION["system_unit"]]
        ])
        put_markdown(f'### Default location:')
        put_table([
            ['Timezone Code', CONFIGURATION["default_location"]["timezone"]["code"]],
            ['City', CONFIGURATION["default_location"]["city"]["name"]],
            ['State', CONFIGURATION["default_location"]["city"]["state"]["name"]],
            ['Country', CONFIGURATION["default_location"]["city"]["state"]["country"]["name"]],
            ['Country Code', CONFIGURATION["default_location"]["city"]["state"]["country"]["code"]],
            ['Latitude', CONFIGURATION["default_location"]["coordinate"]["latitude"]],
            ['Longitude', CONFIGURATION["default_location"]["coordinate"]["longitude"]]
        ])

    auth = 'Enable device auth' if not CONFIGURATION["skip_auth"] else 'Disable device auth'

    buttons = [{'label': auth, 'value': "auth"},
               {'label': 'Set default location', 'value': "geo"},
               {'label': 'Set default voice', 'value': "tts"},
               {'label': 'Set default wake word', 'value': "ww"},
               {'label': 'Set default email', 'value': "email"},
               {'label': 'Set default date format', 'value': "date"},
               {'label': 'Set default time format', 'value': "time"},
               {'label': 'Set default system units', 'value': "unit"}
               ]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    if CONFIGURATION["override_location"]:
        buttons.insert(-2, {'label': 'Enable IP geolocation', 'value': "ip_geo"})
    else:
        buttons.insert(-2, {'label': 'Enable location override', 'value': "loc_override"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    elif opt == "tts":
        tts = select("Choose a voice", list(CONFIGURATION["tts_configs"].keys()))
        CONFIGURATION["default_tts"] = tts
        with popup(f"Default TTS set to: {tts}"):
            put_code(json.dumps(CONFIGURATION["tts_configs"][tts], ensure_ascii=True, indent=2), "json")
    elif opt == "ww":
        ww = select("Choose a wake word",
                    list(CONFIGURATION["ww_configs"].keys()))
        CONFIGURATION["default_ww"] = ww
        with popup(f"Default wake word set to: {ww}"):
            put_code(json.dumps(CONFIGURATION["ww_configs"][ww], ensure_ascii=True, indent=2), "json")
    elif opt == "geo":
        loc = textarea("Enter an address",
                       placeholder="Anywhere street Any city Nº234",
                       required=True)
        data = get_location_config(loc)
        CONFIGURATION["default_location"] = data
        with popup(f"Default location set to: {loc}"):
            put_code(json.dumps(data, ensure_ascii=True, indent=2), "json")
    elif opt == "loc_override":
        CONFIGURATION["override_location"] = True
        CONFIGURATION["geolocate"] = False
        popup("Location override enabled!")
    elif opt == "ip_geo":
        CONFIGURATION["geolocate"] = True
        CONFIGURATION["override_location"] = False
        popup("IP Geolocation enabled!")
    elif opt == "auth":
        CONFIGURATION["skip_auth"] = not CONFIGURATION["skip_auth"]
        if CONFIGURATION["skip_auth"]:
            popup("Device authentication enabled!")
        else:
            popup("Device authentication disabled! Pairing will not be needed")
    elif opt == "date":
        CONFIGURATION["date_format"] = select("Change date format",
                                              ['DMY', 'MDY'])
        popup(f"Default date format set to: {CONFIGURATION['date_format']}")
    elif opt == "time":
        CONFIGURATION["time_format"] = select("Change time format",
                                              ['full', 'short'])
        popup(f"Default time format set to: {CONFIGURATION['time_format']}")
    elif opt == "unit":
        CONFIGURATION["system_unit"] = select("Change system units",
                                              ['metric', 'imperial'])
        popup(f"Default system units set to: {CONFIGURATION['system_unit']}")
    elif opt == "email":
        email = textarea("Enter default notifications email",
                         placeholder="notify@me.com",
                         required=True)
        CONFIGURATION["email"]["recipient"] = email

    if opt != "view":
        CONFIGURATION.store()
    backend_menu(back_handler=back_handler)
