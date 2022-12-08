import json
import os
import time
from uuid import uuid4

from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.database.settings import DeviceDatabase
from ovos_local_backend.utils import generate_code
from ovos_local_backend.utils.geolocate import get_location_config
from pywebio.input import textarea, select, actions, checkbox
from pywebio.output import put_text, put_table, put_markdown, popup, put_code, use_scope, put_image


def device_menu(uuid, back_handler=None):
    buttons = [{'label': "View device configuration", 'value': "view"},
               {'label': "View device location", 'value': "view_loc"},
               {'label': "View device identity", 'value': "identity"},
               {'label': 'Change device name', 'value': "name"},
               {'label': 'Change placement', 'value': "location"},
               {'label': 'Change geographical location', 'value': "geo"},
               {'label': 'Change wake word', 'value': "ww"},
               {'label': 'Change voice', 'value': "tts"},
               {'label': 'Change email', 'value': "email"},
               {'label': 'Change opt-in', 'value': "opt-in"},
               {'label': 'Change date format', 'value': "date"},
               {'label': 'Change time format', 'value': "time"},
               {'label': 'Change system units', 'value': "unit"},
               {'label': 'Delete device', 'value': "delete"}]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    def update_info(d, l=False):
        with use_scope("main_view", clear=True):
            if l:
                put_markdown(f'### Geolocation:')
                put_table([
                    ['City', d.location["city"]["name"]],
                    ['State', d.location["city"]["state"]["name"]],
                    ['Country', d.location["city"]["state"]["country"]["name"]],
                    ['Country Code', d.location["city"]["state"]["country"]["code"]],
                    ['Latitude', d.location["coordinate"]["latitude"]],
                    ['Longitude', d.location["coordinate"]["longitude"]],
                    ['Timezone Code', d.location["timezone"]["code"]]
                ])
            else:
                put_markdown(f'### Configuration:')
                put_table([
                    ['Name', d.name],
                    ['Location', d.device_location],
                    ['Email', d.email],
                    ['Date Format', d.date_format],
                    ['Time Format', d.time_format],
                    ['System Unit', d.system_unit],
                    ['Opt In', d.opt_in],
                    ['Selene Blocked', uuid in CONFIGURATION["selene"]["opt_in_blacklist"]],
                    ['Lang', d.lang],
                    ['Default Wake Word', d.default_ww],
                    ['Default Voice', d.default_tts]
                ])

    db = DeviceDatabase()
    device = db.get_device(uuid)
    if device:
        y = False
        opt = actions(label="What would you like to do?",
                      buttons=buttons)

        if opt == "main":
            with use_scope("main_view", clear=True):
                pass
            device_select(back_handler=back_handler)
            return
        elif opt == "delete":
            with popup("Are you sure you want to delete the device?"):
                put_text("this can not be undone, proceed with caution!")
                y = actions(label="Delete device?",
                            buttons=[{'label': "yes", 'value': True},
                                     {'label': "no", 'value': False}])
                if y:
                    db.delete_device(uuid)
                    db.store()
        elif opt == "opt-in":
            opt_in = checkbox("Open Dataset - device metrics and speech recordings",
                              [{'label': 'Store metrics and recordings',
                                'selected': device.opt_in,
                                'value': "opt_in"},
                               {'label': 'Block Selene sharing',
                                'selected': uuid in CONFIGURATION["selene"]["opt_in_blacklist"],
                                'value': "blacklist"}])

            device.opt_in = "opt_in" in opt_in
            if "blacklist" in opt_in:
                if uuid not in CONFIGURATION["selene"]["opt_in_blacklist"]:
                    CONFIGURATION["selene"]["opt_in_blacklist"].append(uuid)
                    CONFIGURATION.store()
            else:
                if uuid in CONFIGURATION["selene"]["opt_in_blacklist"]:
                    CONFIGURATION["selene"]["opt_in_blacklist"].remove(uuid)
                    CONFIGURATION.store()
        elif opt == "tts":
            tts = select("Choose a voice",
                         list(CONFIGURATION["tts_configs"].keys()))
            device.default_tts = CONFIGURATION["tts_configs"][tts]["module"]
            device.default_tts_cfg = CONFIGURATION["tts_configs"][tts]
        elif opt == "ww":
            ww = select("Choose a wake word",
                        list(CONFIGURATION["ww_configs"].keys()))
            device.default_ww = ww
            device.default_ww_cfg = CONFIGURATION["ww_configs"][ww]
        elif opt == "date":
            date = select("Change date format",
                          ['DMY', 'MDY'])
            device.date_format = date
        elif opt == "time":
            tim = select("Change time format",
                         ['full', 'short'])
            device.time_format = tim
        elif opt == "unit":
            unit = select("Change system units",
                          ['metric', 'imperial'])
            device.system_unit = unit
        elif opt == "email":
            email = textarea("Enter your device email",
                             placeholder="notify@me.com",
                             required=True)
            device.email = email
        elif opt == "name":
            name = textarea("Enter your device name",
                            placeholder="OVOS Mark2",
                            required=True)
            device.name = name
        elif opt == "location":
            loc = textarea("Enter your device placement",
                           placeholder="kitchen",
                           required=True)
            device.device_location = loc
        elif opt == "geo":
            loc = textarea("Enter an address",
                           placeholder="Anywhere street Any city Nº234",
                           required=True)
            data = get_location_config(loc)
            device.location = data
        elif opt == "identity":
            identity = {"uuid": device.uuid,
                        "expires_at": time.time() + 99999999999999,
                        "accessToken": device.token,
                        "refreshToken": device.token}
            with use_scope("main_view", clear=True):
                put_markdown(f'### identity2.json')
                put_code(json.dumps(identity, indent=4), "json")
        elif opt == "view_loc" or opt == "geo":
            update_info(device, True)
        else:
            update_info(device, False)

        if opt not in ["identity", "delete", "view_loc"]:
            db.update_device(device)
            db.store()
            popup("Device updated!")
        elif opt == "delete" and y:
            uuid = None
        device_menu(uuid, back_handler=back_handler)

    else:
        with use_scope("main_view", clear=True):
            pass
        device_select(back_handler=back_handler)


def device_select(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/devices.png', 'rb').read()
        put_image(img)

    devices = {uuid: f"{device['name']}@{device['device_location']}"
               for uuid, device in DeviceDatabase().items()}
    buttons = [{'label': d, 'value': uuid} for uuid, d in devices.items()] + \
              [{'label': 'Delete device database', 'value': "delete_devices"}]
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    if devices:
        uuid = actions(label="What device would you like to manage?",
                       buttons=buttons)
        if uuid == "main":
            with use_scope("main_view", clear=True):
                if back_handler:
                    back_handler()
            return
        elif uuid == "delete_devices":
            with popup("Are you sure you want to delete the device database?"):
                put_text("this can not be undone, proceed with caution!")
                put_text("ALL devices will be unpaired")
            opt = actions(label="Delete devices database?",
                          buttons=[{'label': "yes", 'value': True},
                                   {'label': "no", 'value': False}])
            if opt:
                os.remove(DeviceDatabase().path)
                with use_scope("main_view", clear=True):
                    if back_handler:
                        back_handler()
            else:
                device_select(back_handler)
            return
        else:
            device_menu(uuid, back_handler=back_handler)
    else:
        popup("No devices paired yet!")
        if back_handler:
            with use_scope("main_view", clear=True):
                if back_handler:
                    back_handler()


def instant_pair(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/devices.png', 'rb').read()
        put_image(img)

    uuid = str(uuid4())
    code = generate_code()
    token = f"{code}:{uuid}"
    # add device to db
    with DeviceDatabase() as db:
        db.add_device(uuid, token)

    with use_scope("main_view", clear=True):
        put_markdown("# Device paired!")
        put_table([
            ['UUID', uuid],
            ['CODE', code],
            ['TOKEN', token]
        ])

    device_menu(uuid, back_handler=back_handler)
