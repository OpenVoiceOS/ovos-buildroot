import json
import os

from oauthlib.oauth2 import WebApplicationClient
from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.database.oauth import OAuthApplicationDatabase, OAuthTokenDatabase
from pywebio.input import actions, input_group, input, TEXT
from pywebio.output import use_scope, popup, put_image, put_link, put_code, put_text, put_table, put_markdown


def get_oauth_data(app_id=None):
    data = {}
    if app_id:
        data = OAuthApplicationDatabase().get(app_id)
    data = data or {'auth_endpoint': "https://",
                    'token_endpoint': "https://",
                    'refresh_endpoint': "https://"}
    if "callback_endpoint" not in data:
        backend_url = f"http://0.0.0.0:{CONFIGURATION['backend_port']}/{CONFIGURATION['api_version']}"
        data["callback_endpoint"] = f"{backend_url}/auth/callback/{app_id or '...'}"

    with use_scope("main_view", clear=True):
        return input_group('Settings', [
            input("Name", value=app_id or "...",
                  type=TEXT, name="oauth_service"),
            input("Client ID", value=data.get("client_id", ""),
                  type=TEXT, name='client_id'),
            input("Client Secret", value=data.get("client_secret", ""),
                  type=TEXT, name='client_secret'),
            input("Auth Endpoint", value=data.get("auth_endpoint", ""),
                  type=TEXT, name='auth_endpoint'),
            input("Token Endpoint", value=data.get("token_endpoint", ""),
                  type=TEXT, name='token_endpoint'),
            input("Refresh Endpoint", value=data.get("refresh_endpoint", ""),
                  type=TEXT, name='refresh_endpoint'),
            input("Callback Endpoint", value=data["callback_endpoint"],
                  type=TEXT, name='callback_endpoint'),
            input("Scope", value=data.get("scope", ""),
                  type=TEXT, name='scope')
        ])


def authorize_app(data):
    callback_endpoint = f"http://0.0.0.0:36535/auth/callback/{data['oauth_service']}"
    client = WebApplicationClient(data["client_id"])
    request_uri = client.prepare_request_uri(
        data["auth_endpoint"],
        redirect_uri=data.get("callback_endpoint") or callback_endpoint,
        show_dialog=True,
        state=data['oauth_service'],
        scope=data["scope"],
    )
    with popup(f"{data['oauth_service']}"):
        put_link("Authorize", request_uri, new_window=True)


def _render_app(app_id):
    with use_scope("main_view", clear=True):
        data = OAuthApplicationDatabase()[app_id]

        put_markdown(f'# {app_id.title()}')
        put_table([
            ['Client ID', data["client_id"]],
            ['Client Secret', data["client_secret"]],
            ['Scope', data["scope"]]
        ])
        put_markdown(f'### OAuth Endpoints')
        put_table([
            ['Auth', data["auth_endpoint"]],
            ['Token', data["token_endpoint"]],
            ['Refresh', data["refresh_endpoint"]],
            ['Callback', data["callback_endpoint"]],
        ])


def app_menu(app_id, back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/oauth.png', 'rb').read()
        put_image(img)

    _render_app(app_id)

    buttons = [
        {'label': "Configure", 'value': "oauth"},
    ]
    tok = OAuthTokenDatabase().get(app_id)
    if tok:
        buttons.append({'label': "View Token", 'value': "token"})
        buttons.append({'label': "Refresh Token", 'value': "refresh"})
    else:
        buttons.append({'label': "Authorize", 'value': "auth"})
    buttons.append({'label': "Delete", 'value': "delete"})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label=f"What would you like to do with {app_id}?",
                  buttons=buttons)
    if opt == "main":
        with use_scope("main_view", clear=True):
            oauth_menu(back_handler=back_handler)
        return
    elif opt == "token":
        with popup("OAuth Token"):
            put_code(json.dumps(tok, indent=4), language="json")
    elif opt == "auth" or opt == "refresh":  # TODO special refresh handling (?)
        data = OAuthApplicationDatabase()[app_id]
        authorize_app(data)
    elif opt == "oauth":
        data = get_oauth_data(app_id)

        with OAuthApplicationDatabase() as db:
            db[data["oauth_service"]] = data

        with popup(app_id):
            put_text(f"{app_id} oauth settings updated!")

    elif opt == "delete":
        db = OAuthApplicationDatabase()
        if app_id in db:
            db.pop(app_id)
            db.store()
        with popup(app_id):
            put_text(f"{app_id} oauth settings deleted!")
        oauth_menu(back_handler=back_handler)
        return
    else:
        app_id = opt

    app_menu(app_id, back_handler=back_handler)


def oauth_menu(back_handler=None):
    with use_scope("logo", clear=True):
        img = open(f'{os.path.dirname(__file__)}/res/oauth.png', 'rb').read()
        put_image(img)

    with use_scope("main_view", clear=True):
        pass

    buttons = [{'label': 'New App', 'value': "new"}]
    for app, data in OAuthApplicationDatabase().items():
        buttons.append({'label': app, 'value': app})
    if back_handler:
        buttons.insert(0, {'label': '<- Go Back', 'value': "main"})

    opt = actions(label="What would you like to do?",
                  buttons=buttons)
    if opt == "new":
        data = get_oauth_data()

        with OAuthApplicationDatabase() as db:
            db.add_application(data["oauth_service"],
                               data["client_id"],
                               data["client_secret"],
                               data["auth_endpoint"],
                               data["token_endpoint"],
                               data["refresh_endpoint"],
                               data["scope"])

        authorize_app(data)

    elif opt == "main":
        with use_scope("main_view", clear=True):
            if back_handler:
                back_handler()
        return
    else:
        app_menu(opt, back_handler=back_handler)
        return

    oauth_menu(back_handler=back_handler)
