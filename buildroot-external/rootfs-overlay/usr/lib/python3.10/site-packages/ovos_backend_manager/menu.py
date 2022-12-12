from ovos_local_backend.configuration import CONFIGURATION
from pywebio.input import textarea, actions
from pywebio.output import put_text, popup, use_scope, put_image

from ovos_backend_manager.backend import backend_menu
from ovos_backend_manager.datasets import datasets_menu
from ovos_backend_manager.devices import device_select, instant_pair
from ovos_backend_manager.metrics import metrics_menu
from ovos_backend_manager.microservices import microservices_menu
from ovos_backend_manager.oauth import oauth_menu
from ovos_backend_manager.selene import selene_menu


def main_menu():
    with use_scope("logo", clear=True):
        from os.path import dirname
        img = open(f'{dirname(__file__)}/res/personal_backend.png', 'rb').read()
        put_image(img)

    opt = actions(label="What would you like to do?",
                  buttons=[{'label': 'Pair a device', 'value': "pair"},
                           {'label': 'Manage Devices', 'value': "device"},
                           {'label': 'Manage Metrics', 'value': "metrics"},
                           {'label': 'Manage Datasets', 'value': "db"},
                           {'label': 'OAuth Applications', 'value': "oauth"},
                           {'label': 'Configure Backend', 'value': "backend"},
                           {'label': 'Configure Microservices', 'value': "services"},
                           {'label': 'Configure Selene Proxy', 'value': "selene"}])
    if opt == "pair":
        instant_pair(back_handler=main_menu)
    elif opt == "services":
        microservices_menu(back_handler=main_menu)
    elif opt == "oauth":
        oauth_menu(back_handler=main_menu)
    elif opt == "db":
        datasets_menu(back_handler=main_menu)
    elif opt == "backend":
        backend_menu(back_handler=main_menu)
    elif opt == "selene":
        selene_menu(back_handler=main_menu)
    elif opt == "device":
        device_select(back_handler=main_menu)
    elif opt == "metrics":
        metrics_menu(back_handler=main_menu)


def prompt_admin_key():
    admin_key = textarea("insert your admin_key, this should have been set in your backend configuration file",
                         placeholder="SuperSecretPassword1!",
                         required=True)
    if CONFIGURATION["admin_key"] != admin_key:
        popup("INVALID ADMIN KEY!")
        prompt_admin_key()


def start():
    if not CONFIGURATION["admin_key"]:
        put_text("This personal backend instance does not have the admin interface exposed")
        exit(1)
    with use_scope("logo", clear=True):
        from os.path import dirname
        img = open(f'{dirname(__file__)}/res/personal_backend.png', 'rb').read()
        put_image(img)

    prompt_admin_key()
    main_menu()
