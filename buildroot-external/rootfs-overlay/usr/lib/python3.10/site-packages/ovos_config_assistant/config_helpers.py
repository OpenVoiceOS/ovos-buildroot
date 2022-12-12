from ovos_config import get_ovos_config
from ovos_config.meta import get_ovos_default_config_paths


def pprint_ovos_conf():
    print("\n## OVOS Configuration")

    paths = get_ovos_default_config_paths()
    ovos_conf = get_ovos_config()

    print("     ovos.conf exists          :", bool(paths))
    if paths:
        for p in paths:
            print("         ", p)
    print("     xdg compliance            :", ovos_conf["xdg"])
    print("     base xdg folder           :", ovos_conf["base_folder"])
    print("     mycroft config filename   :", ovos_conf["config_filename"])
    print("     default mycroft.conf path :")
    print("         ", ovos_conf["default_config_path"])


if __name__ == "__main__":
    pprint_ovos_conf()
    """
    ## OVOS Configuration
     ovos.conf exists          : True
          /home/user/.config/OpenVoiceOS/ovos.conf
     xdg compliance            : True
     base xdg folder           : mycroft
     mycroft config filename   : mycroft.conf
     default mycroft.conf path :
          /home/user/ovos-core/.venv/lib/python3.9/site-packages/mycroft/configuration/mycroft.conf
    """
