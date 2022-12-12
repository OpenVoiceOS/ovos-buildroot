"""This file will check a system level OpenVoiceOS specific config file

The ovos config is json with comment support like the regular mycroft.conf

Default locations tried by order until a file is found
- /etc/OpenVoiceOS/ovos.conf
- /etc/mycroft/ovos.conf

XDG locations are then merged over the select default config (if found)

Examples config:

{
   // the "name of the core",
   //         eg, OVOS, Neon, Chatterbox...
   //  all XDG paths should respect this
   //        {xdg_path}/{base_folder}/some_resource
   "base_folder": "OpenVoiceOS",

   // the filename of "mycroft.conf",
   //      eg, ovos.conf, chatterbox.conf, neon.conf...
   // "mycroft.conf" paths are derived from this
   //        {xdg_path}/{base_folder}/{config_filename}
   "config_filename": "mycroft.conf",

   // override the default.conf location, allows changing the default values
   //     eg, disable backend, disable skills, configure permissions
   "default_config_path": "/etc/OpenVoiceOS/default_mycroft.conf",

   // this is intended for derivative products, if ovos is being imported 
   // from one of these modules then the values below will be used instead
   //     eg, mycroft/ovos/neon can coexist in the same machine
   "module_overrides": {
        "neon_core": {
            "base_folder": "neon",
            "config_filename": "neon.conf",
            "default_config_path": "/opt/neon/neon.conf"
        }
   },
   // essentially aliases for the above, useful for microservice architectures
   "submodule_mappings": {
        "neon_speech": "neon_core",
        "neon_audio": "neon_core",
        "neon_enclosure": "neon_core"
   }
}
"""
from os.path import isfile, join, dirname

from json_database import JsonStorage

import ovos_config.locations as _oloc
from ovos_utils.json_helper import load_commented_json, merge_dict
from ovos_utils.log import LOG
from ovos_utils.system import is_running_from_module


def get_ovos_config():
    """ load ovos.conf
    goes trough all possible ovos.conf paths and loads them in order

    submodule overrides are applied to the final config if overrides are defined for the caller module
        eg, if neon-core is calling this method then neon config overrides are loaded

    """
    # populate default values
    config = {"xdg": True,
              "base_folder": "mycroft",
              "config_filename": "mycroft.conf"}
    try:
        config["default_config_path"] = _oloc.find_default_config()
    except FileNotFoundError:  # not a mycroft device
        config["default_config_path"] = join(dirname(__file__), "mycroft.conf")

    # load ovos.conf
    for path in get_ovos_default_config_paths():
        try:
            config = merge_dict(config, load_commented_json(path))
        except:
            # tolerate bad json TODO proper exception (?)
            pass

    # let's check for derivatives specific configs
    # the assumption is that these cores are exclusive to each other,
    # this will never find more than one override
    # TODO this works if using dedicated .venvs what about system installs?
    cores = config.get("module_overrides") or {}
    for k in cores:
        if is_running_from_module(k):
            config = merge_dict(config, cores[k])
            break
    else:
        subcores = config.get("submodule_mappings") or {}
        for k in subcores:
            if is_running_from_module(k):
                config = merge_dict(config, cores[subcores[k]])
                break

    return config


def save_ovos_config(new_config):
    """ update ovos.conf contents at ~/.config/OpenVoiceOS/ovos.conf """
    OVOS_CONFIG = join(_oloc.get_xdg_config_save_path("OpenVoiceOS"),
                       "ovos.conf")
    cfg = JsonStorage(OVOS_CONFIG)
    cfg.update(new_config)
    cfg.store()
    return cfg


def get_ovos_default_config_paths():
    """ return a list of all existing ovos.conf file locations by order of precedence

     eg. ["/etc/OpenVoiceOS/ovos.conf", "/home/user/.config/OpenVoiceOS/ovos.conf"]

     """
    paths = []
    if isfile("/etc/OpenVoiceOS/ovos.conf"):
        paths.append("/etc/OpenVoiceOS/ovos.conf")
    elif isfile("/etc/mycroft/ovos.conf"):
        LOG.warning("found /etc/mycroft/ovos.conf\n"
                    "This location has been DEPRECATED!\n"
                    "Please move your config to /etc/OpenVoiceOS/ovos.conf")
        paths.append("/etc/mycroft/ovos.conf")

    # This includes both the user config and
    # /etc/xdg/OpenVoiceOS/ovos.conf
    for p in _oloc.get_xdg_config_dirs("OpenVoiceOS"):
        if isfile(join(p, "ovos.conf")):
            paths.append(join(p, "ovos.conf"))

    return paths


def is_using_xdg():
    """ BACKWARDS COMPAT: logs warning and always returns True"""
    LOG.warning("is_using_xdg has been deprecated! XDG specs are always honoured, this method will be removed in a future release")
    return True


def get_xdg_base():
    """ base folder name to be used when building paths of the format {$XDG_XXX}/{base}

    different derivative cores may change this folder, this value is derived from ovos.conf
        eg, "mycroft", "hivemind", "neon" ....
    """

    return get_ovos_config().get("base_folder") or "mycroft"


def set_xdg_base(folder_name):
    """ base folder name to be used when building paths of the format {$XDG_XXX}/{base}

    different derivative cores may change this folder, this value is derived from ovos.conf
        eg, "mycroft", "hivemind", "neon" ....

    NOTE: this value will be set globally, per core overrides in ovos.conf take precedence
    """
    LOG.info(f"XDG base folder set to: '{folder_name}'")
    save_ovos_config({"base_folder": folder_name})


def set_config_filename(file_name, core_folder=None):
    """ base config file name to be used when building paths

    different derivative cores may change this filename, this value is derived from ovos.conf
        eg, "mycroft.conf", "hivemind.json", "neon.yaml" ....

    NOTE: this value will be set globally, per core overrides in ovos.conf take precedence
    """
    if core_folder:
        set_xdg_base(core_folder)
    LOG.info(f"config filename set to: '{file_name}'")
    save_ovos_config({"config_filename": file_name})


def get_config_filename():
    """ base config file name to be used when building paths

    different derivative cores may change this filename, this value is derived from ovos.conf
        eg, "mycroft.conf", "hivemind.json", "neon.yaml" ....
    """
    return get_ovos_config().get("config_filename") or "mycroft.conf"


def set_default_config(file_path=None):
    """ full path to default config file to be used
    NOTE: this is a full path, not a directory! "config_filename" parameter is not used here

    different derivative cores may change this file, this value is derived from ovos.conf

    NOTE: this value will be set globally, per core overrides in ovos.conf take precedence
    """
    file_path = file_path or _oloc.find_default_config()
    LOG.info(f"default config file changed to: {file_path}")
    save_ovos_config({"default_config_path": file_path})
