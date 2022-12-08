from os.path import dirname

from ovos_config import Configuration
from pywebio.input import textarea, actions
from pywebio.output import put_text, popup, use_scope, put_image

from ovos_config_assistant.backend import backend_menu
from ovos_config_assistant.datasets import datasets_menu
from ovos_config_assistant.metrics import metrics_menu
from ovos_config_assistant.microservices import microservices_menu
from ovos_config_assistant.oauth import oauth_menu
from ovos_config_assistant.plugins import plugins_menu


def main_menu():
    with use_scope("logo", clear=True):
        from os.path import dirname
        img = open(f'{dirname(__file__)}/res/OCA.png', 'rb').read()
        put_image(img)

    opt = actions(label="What would you like to do?",
                  buttons=[{'label': 'Manage Metrics', 'value': "metrics"},
                           {'label': 'Manage Datasets', 'value': "db"},
                           {'label': 'OAuth Applications', 'value': "oauth"},
                           {'label': 'Configure Backend', 'value': "backend"},
                           {'label': 'Configure Plugins', 'value': "plugins"},
                           {'label': 'Configure Microservices', 'value': "services"}])
    if opt == "services":
        microservices_menu(back_handler=main_menu)
    elif opt == "oauth":
        oauth_menu(back_handler=main_menu)
    elif opt == "db":
        datasets_menu(back_handler=main_menu)
    elif opt == "backend":
        backend_menu(back_handler=main_menu)
    elif opt == "plugins":
        plugins_menu(back_handler=main_menu)
    elif opt == "metrics":
        metrics_menu(back_handler=main_menu)


def prompt_admin_key():
    admin_key = textarea("insert your admin_key, this should have been set in your ovos configuration file",
                         placeholder="SuperSecretPassword1!",
                         required=True)
    if Configuration()["admin_key"] != admin_key:
        popup("INVALID ADMIN KEY!")
        prompt_admin_key()


def start():
    with use_scope("logo", clear=True):
        img = open(f'{dirname(__file__)}/res/OCA.png', 'rb').read()
        put_image(img)
    cfg = Configuration()
    # cfg["admin_key"] = "123"
    if not cfg.get("admin_key"):
        put_text("This OpenVoiceOS instance does not have the admin interface exposed")
        return
    prompt_admin_key()
    main_menu()
