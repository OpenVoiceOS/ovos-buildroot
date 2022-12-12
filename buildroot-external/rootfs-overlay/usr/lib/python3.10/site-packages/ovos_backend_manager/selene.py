import json
import os

from ovos_local_backend.configuration import CONFIGURATION
from pywebio.input import actions, file_upload, input_group, textarea
from pywebio.output import put_table, popup, use_scope, put_image, put_markdown, put_code


def pairing_menu(back_handler=None):
    version = CONFIGURATION["selene"]["version"]
    host = CONFIGURATION["selene"]["url"]
    ident = CONFIGURATION["selene"]["identity_file"]
    paired = os.path.exists(ident)

    with use_scope("main_view", clear=True):
        put_markdown("# Status")
        put_table([
            ['Enabled', CONFIGURATION["selene"]["enabled"]],
            ['Host', host],
            ['Version', version],
            ['Identity', ident],
            ['Paired', paired],
            ['Proxy Pairing Enabled', CONFIGURATION["selene"]["proxy_pairing"]]
        ])
        if os.path.isfile(ident):
            with open(ident) as f:
                content = f.read()

            put_markdown("# Identity")
            put_code(content, "json")

    buttons = [{'label': 'Upload identity2.json', 'value': "upload"},
               {'label': 'Paste identity2.json', 'value': "paste"}]
    if os.path.isfile(ident):
        buttons.append({'label': 'Delete identity2.json', 'value': "delete"})

    label = "Enable Proxy Pairing" if not CONFIGURATION["selene"]["proxy_pairing"] else "Disable Proxy Pairing"
    buttons.append({'label': label, 'value': "proxy"})

    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        selene_menu(back_handler=back_handler)
        return
    elif opt == "delete":
        with use_scope("main_view", clear=True):
            if os.path.isfile(ident):
                os.remove(ident)
                popup("Identity deleted!")
            else:
                popup("Identity does not exist!")
    elif opt == "upload":
        with use_scope("main_view", clear=True):
            data = input_group("Upload identity", [
                file_upload("identity file", name="file")
            ])
            mime = data["file"]["mime_type"]
            content = data["file"]["content"]
            if mime != "application/json":
                popup("invalid format!")
            else:
                os.makedirs(os.path.dirname(ident), exist_ok=True)
                with open(ident, "wb") as f:
                    f.write(content)
                with popup("Identity uploaded!"):
                    put_code(content.decode("utf-8"), "json")
    elif opt == "paste":
        with use_scope("main_view", clear=True):
            dummy = """{
        "uuid": "31628fa1-dbfd-4626-aaa2-1464dd204715",
        "expires_at": 100001663862051.53,
        "accessToken": "8YI3NQ:31628fa1-dbfd-4626-aaa2-1464dd204715",
        "refreshToken": "8YI3NQ:31628fa1-dbfd-4626-aaa2-1464dd204715"
    }
    """
            data = textarea("identity2.json", placeholder=dummy, required=True)
            with open(ident, "w") as f:
                f.write(data)
            with popup("Identity updated!"):
                put_code(data, "json")
    elif opt == "proxy":
        CONFIGURATION["selene"]["proxy_pairing"] = not CONFIGURATION["selene"]["proxy_pairing"]
        CONFIGURATION.store()
    pairing_menu(back_handler=back_handler)


def account_menu(back_handler=None):
    version = CONFIGURATION["selene"]["version"]
    host = CONFIGURATION["selene"]["url"]
    ident = CONFIGURATION["selene"]["identity_file"]
    paired = os.path.exists(ident)
    uuid = None
    if paired:
        with open(ident) as f:
            uuid = json.load(f)["uuid"]

    with use_scope("main_view", clear=True):
        put_markdown("# Account")
        put_table([
            ['Selene UUID', uuid],
            ['Download Location', CONFIGURATION["selene"]["download_location"]],
            ['Download Preferences', CONFIGURATION["selene"]["download_prefs"]],
            ['Download Skill Settings', CONFIGURATION["selene"]["download_settings"]],
            ['Upload Skill Settings', CONFIGURATION["selene"]["upload_settings"]],
            ['Force 2 way Skill Settings sync', CONFIGURATION["selene"]["force2way"]]
        ])

    buttons = []
    label = "Enable Location Download" if not CONFIGURATION["selene"][
        "download_location"] else "Disable Location Download"
    buttons.append({'label': label, 'value': "location"})
    label = "Enable Preferences Download" if not CONFIGURATION["selene"][
        "download_prefs"] else "Disable Preferences Download"
    buttons.append({'label': label, 'value': "prefs"})
    label = "Enable SkillSettings Download" if not CONFIGURATION["selene"][
        "download_settings"] else "Disable SkillSettings Download"
    buttons.append({'label': label, 'value': "download_settings"})
    label = "Enable SkillSettings Upload" if not CONFIGURATION["selene"][
        "upload_settings"] else "Disable SkillSettings Upload"
    buttons.append({'label': label, 'value': "upload_settings"})
    label = "Enable forced 2way sync" if not CONFIGURATION["selene"]["force2way"] else "Disable forced 2way sync"
    buttons.append({'label': label, 'value': "2way"})

    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)

    if opt == "main":
        selene_menu(back_handler=back_handler)
        return
    elif opt == "location":
        CONFIGURATION["selene"]["download_location"] = not CONFIGURATION["selene"]["download_location"]
    elif opt == "prefs":
        CONFIGURATION["selene"]["download_prefs"] = not CONFIGURATION["selene"]["download_prefs"]
    elif opt == "download_settings":
        CONFIGURATION["selene"]["download_settings"] = not CONFIGURATION["selene"]["download_settings"]
    elif opt == "upload_settings":
        CONFIGURATION["selene"]["upload_settings"] = not CONFIGURATION["selene"]["upload_settings"]
    elif opt == "2way":
        CONFIGURATION["selene"]["force2way"] = not CONFIGURATION["selene"]["force2way"]

    CONFIGURATION.store()
    account_menu(back_handler=back_handler)


def integrations_menu(back_handler=None):
    version = CONFIGURATION["selene"]["version"]
    host = CONFIGURATION["selene"]["url"]
    ident = CONFIGURATION["selene"]["identity_file"]
    paired = os.path.exists(ident)
    uuid = None
    if paired:
        with open(ident) as f:
            uuid = json.load(f)["uuid"]

    with use_scope("main_view", clear=True):
        put_markdown("# Integrations")
        put_table([
            ['Selene UUID', uuid],
            ['Weather Enabled', CONFIGURATION["selene"]["proxy_weather"]],
            ['WolframAlpha Enabled', CONFIGURATION["selene"]["proxy_wolfram"]],
            ['Geolocation Enabled', CONFIGURATION["selene"]["proxy_geolocation"]],
            ['Email Enabled', CONFIGURATION["selene"]["proxy_email"]]
        ])

    buttons = []
    label = "Enable Weather Proxy" if not CONFIGURATION["selene"]["proxy_weather"] else "Disable Weather Proxy"
    buttons.append({'label': label, 'value': "weather"})
    label = "Enable WolframAlpha Proxy" if not CONFIGURATION["selene"][
        "proxy_wolfram"] else "Disable WolframAlpha Proxy"
    buttons.append({'label': label, 'value': "wolfram"})
    label = "Enable Geolocation Proxy" if not CONFIGURATION["selene"][
        "proxy_geolocation"] else "Disable Geolocation Proxy"
    buttons.append({'label': label, 'value': "geolocation"})
    label = "Enable Email Proxy" if not CONFIGURATION["selene"]["proxy_email"] else "Disable Email Proxy"
    buttons.append({'label': label, 'value': "email"})

    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)

    if opt == "main":
        selene_menu(back_handler=back_handler)
        return
    elif opt == "geolocation":
        CONFIGURATION["selene"]["proxy_geolocation"] = not CONFIGURATION["selene"]["proxy_geolocation"]
    elif opt == "weather":
        CONFIGURATION["selene"]["proxy_weather"] = not CONFIGURATION["selene"]["proxy_weather"]
    elif opt == "wolfram":
        CONFIGURATION["selene"]["proxy_wolfram"] = not CONFIGURATION["selene"]["proxy_wolfram"]
    elif opt == "email":
        CONFIGURATION["selene"]["proxy_email"] = not CONFIGURATION["selene"]["proxy_email"]

    CONFIGURATION.store()
    integrations_menu(back_handler=back_handler)


def dataset_menu(back_handler=None):
    version = CONFIGURATION["selene"]["version"]
    host = CONFIGURATION["selene"]["url"]
    ident = CONFIGURATION["selene"]["identity_file"]
    paired = os.path.exists(ident)

    with use_scope("main_view", clear=True):
        put_markdown("# Open Dataset")
        put_table([
            ['Opt In', CONFIGURATION["selene"]["opt_in"]],
            ['Upload Metrics', CONFIGURATION["selene"]["upload_metrics"]],
            ['Upload Wake Words', CONFIGURATION["selene"]["upload_wakewords"]],
            ['Upload Utterances', CONFIGURATION["selene"]["upload_utterances"]]
        ])

    buttons = []
    label = "Enable Open Dataset Opt In" if not CONFIGURATION["selene"]["opt_in"] else "Disable Open Dataset Opt In"
    buttons.append({'label': label, 'value': "opt_in"})
    label = "Enable Metrics Upload" if not CONFIGURATION["selene"]["upload_metrics"] else "Disable Metrics Upload"
    buttons.append({'label': label, 'value': "metrics"})
    label = "Enable Wake Words Upload" if not CONFIGURATION["selene"][
        "upload_wakewords"] else "Disable Wake Words Upload"
    buttons.append({'label': label, 'value': "ww"})
    label = "Enable Utterances Upload" if not CONFIGURATION["selene"][
        "upload_utterances"] else "Disable Utterances Upload"
    buttons.append({'label': label, 'value': "stt"})

    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)

    if opt == "main":
        selene_menu(back_handler=back_handler)
        return
    elif opt == "opt_in":
        CONFIGURATION["selene"]["opt_in"] = not CONFIGURATION["selene"]["opt_in"]
    elif opt == "selene":
        CONFIGURATION["selene"]["enabled"] = not CONFIGURATION["selene"]["enabled"]
    elif opt == "stt":
        CONFIGURATION["selene"]["upload_utterances"] = not CONFIGURATION["selene"]["upload_utterances"]
    elif opt == "ww":
        CONFIGURATION["selene"]["upload_wakewords"] = not CONFIGURATION["selene"]["upload_wakewords"]
    elif opt == "metrics":
        CONFIGURATION["selene"]["upload_metrics"] = not CONFIGURATION["selene"]["upload_metrics"]

    CONFIGURATION.store()
    dataset_menu(back_handler=back_handler)


def selene_menu(back_handler=None):
    version = CONFIGURATION["selene"]["version"]
    host = CONFIGURATION["selene"]["url"]
    ident = CONFIGURATION["selene"]["identity_file"]
    paired = os.path.exists(ident)

    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/selene_proxy.png', 'rb').read()
        put_image(img)

    with use_scope("main_view", clear=True):
        put_markdown("# Status")
        put_table([
            ['Enabled', CONFIGURATION["selene"]["enabled"]],
            ['Host', host]
        ])

    buttons = [{'label': 'Manage Identity', 'value': "pair"},
               {'label': 'Manage Account', 'value': "account"},
               {'label': 'Manage Integrations', 'value': "integrations"},
               {'label': 'Manage Open Dataset', 'value': "dataset"}]

    if CONFIGURATION["selene"]["enabled"]:
        buttons.insert(0, {'label': "Disable Selene", 'value': "selene"})
    else:
        buttons.insert(0, {'label': "Enable Selene", 'value': "selene"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    elif opt == "pair":
        pairing_menu(back_handler=back_handler)
        return
    elif opt == "account":
        account_menu(back_handler=back_handler)
        return
    elif opt == "integrations":
        integrations_menu(back_handler=back_handler)
        return
    elif opt == "dataset":
        dataset_menu(back_handler=back_handler)
        return
    elif opt == "selene":
        CONFIGURATION["selene"]["enabled"] = not CONFIGURATION["selene"]["enabled"]
        CONFIGURATION.store()

    selene_menu(back_handler=back_handler)
