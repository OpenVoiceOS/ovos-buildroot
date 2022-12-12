import json
import os
from ovos_backend_client.api import AdminApi
from ovos_config import Configuration
from ovos_backend_client.backends import OfflineBackend, \
    SeleneBackend, PersonalBackend, BackendType, get_backend_config, API_REGISTRY
from ovos_backend_client.identity import IdentityManager
from ovos_backend_client.pairing import is_paired

from pywebio.input import actions, file_upload, input_group, textarea, input
from pywebio.output import put_table, popup, use_scope, put_markdown, put_code


def pairing_menu(back_handler=None):
    host, version, ident, backend_type = get_backend_config()
    ident = ident or IdentityManager.IDENTITY_FILE

    with use_scope("main_view", clear=True):
        put_markdown("# Status")
        put_table([
            ['Enabled', not Configuration()["server"].get("disabled")],
            ['Host', host],
            ['Version', version],
            ['Identity', ident],
            ['Paired', is_paired()]
        ])
        if os.path.isfile(ident):
            with open(ident) as f:
                content = json.load(f)

            put_markdown("# Identity")
            put_code(json.dumps(content, indent=4), "json")

    buttons = [{'label': 'Upload identity2.json', 'value': "upload"},
               {'label': 'Paste identity2.json', 'value': "paste"}]
    if os.path.isfile(ident):
        buttons.append({'label': 'Delete identity2.json', 'value': "delete"})
    if backend_type == "personal":
        buttons.append({'label': 'Manual Pairing', 'value': "pair"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?", buttons=buttons)
    if opt == "main":
        if back_handler:
            back_handler()
        return
    elif opt == "pair":
        with use_scope("main_view", clear=True):
            api = AdminApi(input("Admin Key? "))
            ident = IdentityManager.load()
            ident = api.pair(ident.uuid)
            IdentityManager.save(ident)
            with popup("New identity2.json"):
                put_code(json.dumps(ident, indent=4), language="json")
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

    pairing_menu(back_handler=back_handler)
