from os import path
from typing import Union, Optional
from json_database import JsonConfigXDG, JsonStorageXDG
from ovos_utils.json_helper import merge_dict
from ovos_utils.log import LOG
from ovos_skills_manager.appstores.local import get_skills_folder
from ovos_skills_manager.version import CURRENT_OSM_VERSION


def safe_get_skills_folder():
    try:
        return get_skills_folder()
    except Exception as e:
        LOG.error(e)
        return ""


def _existing_osm_config() -> Optional[Union[JsonStorageXDG, JsonConfigXDG]]:
    """NOTE: Use get_config_object() unless you're migrating config!
    
    Tries to locate the OSM config file, first trying the current path,
    and then checking the old location (used by the migration upgrade)

    Returns:
        [JsonConfigXDG|JsonStorageXDG|None]: the existing OSM config, or None
    """
    config = JsonConfigXDG("OVOS-SkillsManager", subfolder="OpenVoiceOS")
    if not path.exists(config.path):
        # Check for legacy config
        config = JsonStorageXDG("OVOS-SkillsManager")
        if not path.exists(config.path):
            return None
    return config


def get_config_object() -> Union[JsonStorageXDG, JsonConfigXDG]:
    """Locates or creates the OSM config file, and ensures that all required
       values are present, inserting defaults as needed

    Returns:
        json_database.JsonConfigXDG: the OSM config object
    """
    config = _existing_osm_config() or \
        JsonConfigXDG("OVOS-SkillsManager", subfolder="OpenVoiceOS")
    default_appstores = {
        "local": {
            "active": True,
            "url": safe_get_skills_folder(),
            "parse_github": False,
            "priority": 1},
        "ovos": {
            "active": True,
            "url": "https://github.com/OpenVoiceOS/OVOS-appstore",
            "parse_github": False,
            "priority": 2},
        "mycroft_marketplace": {
            "active": False,
            "url": "https://market.mycroft.ai/",
            "parse_github": False,
            "priority": 5},
        "pling": {
            "active": False,
            "url": "https://apps.plasma-bigscreen.org/",
            "parse_github": False,
            "priority": 10},
        "neon": {
            "active": False,
            "url": "https://github.com/NeonGeckoCom/neon-skills-submodules/",
            "parse_github": False,
            "auth_token": None,
            "priority": 50},
        "andlo_skill_list": {
            "active": False,
            "url": "https://andlo.gitbook.io/mycroft-skills-list/",
            "parse_github": False,
            "priority": 100}
    }
    if "appstores" not in config:
        # NOTE, below should match Appstore.appstore_id
        config["appstores"] = default_appstores
        config["appstores"] = merge_dict(config["appstores"],
                                         default_appstores,
                                         new_only=True,
                                         no_dupes=True)
    if "version" not in config:
        # This stuff can really only happen on first run
        config["version"] = CURRENT_OSM_VERSION
        config["last_upgrade"] = CURRENT_OSM_VERSION
    config.store()
    return config
