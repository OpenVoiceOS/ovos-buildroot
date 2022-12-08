from collections import OrderedDict
from os import path, remove
from packaging import version

from click import echo
from json_database import JsonConfigXDG, JsonStorageXDG
from ovos_skills_manager.config import _existing_osm_config
from ovos_skills_manager.version import CURRENT_OSM_VERSION

def do_launch_version_checks():
    """ Upon running OSM, perform a sequence of checks to determine:
            1. If OSM is already installed and working
            2. If its config file claims to be the same version as OSM itself
            3. If not, whether any upgrades need to be applied
        and then, if necessary:
            1. Applies the earliest unapplied upgrade and bumps config to that version
            2. Repeat until there are no unapplied upgrades
            3. Bump config to the current version
    """
    config = _existing_osm_config()
    if config: # does the config file exist?
        if not _check_current_version(config): # does it reflect the most recent version?
            echo("OSM has been updated. Checking for upgrades... ", nl=False)
            upgrade, config = _check_upgrade(config) # if not, do the upgrade routine
            if upgrade:
                echo("found")
                echo("Applying OSM upgrades. Please be patient and do not exit!")
                config = _find_and_perform_osm_upgrades(config)
            else:
                echo("none found\nApplying new version number.")
            # now that we've applied all updates, bump config version to current
            config["version"] = CURRENT_OSM_VERSION
            config.store()
            echo(f"OSM is now v{CURRENT_OSM_VERSION}\n")
    # if the config file doesn't exist, this must surely be first run, so don't do anything

def _check_current_version(config:dict=None) -> bool:
    """ Determine the currently-installed version of OSM, or pretend to be
        version 0.0.9, which is older than the oldest marked upgrade
    """
    config = config or _existing_osm_config()
    return version.parse((config.get("version") or "0.0.9")) == version.parse(CURRENT_OSM_VERSION)

def _check_upgrade(config:dict=None) -> (bool, dict):
    """ Determine whether OSM needs to be upgraded. Run by launch checks.

    Returns:
        bool: Whether there are upgrades to be applied
        dict: the existing OSM config object for rereferencing
    """
    config = config or _existing_osm_config()
    # find the last upgrade path that was performed
    last_upgrade = config.get('last_upgrade')
    if not last_upgrade:
        config['last_upgrade'] = 'v0.0.9a5' # 0.0.9 -> 0.0.10 is first-ever upgrade with code
        config.store()
        return True, config # We haven't done the 0.0.10 upgrade yet, so... yeah

    last_upgrade = version.parse(last_upgrade) # cast the version to something we can compare
    upgrade_versions = list(UPGRADE_PATHS.keys())
    if last_upgrade == upgrade_versions[-1]:
        return False, config  # we have done the most recent possible upgrade
    for upgrade_version in upgrade_versions:
        if last_upgrade < upgrade_version:
            return True, config
    return False, config

def _find_and_perform_osm_upgrades(config: JsonStorageXDG) -> JsonStorageXDG:
    """ Accepts and returns config. Iterates over possible upgrades,
        applying the earliest unapplied upgrade and bumping config's version.
        Loops until there are no more upgrades to apply.
        The outermost function will bump config to the current OSM version,
        regardless of whether any upgrades were applied.
    """
    last_upgrade = version.parse(config.get('last_upgrade'))
    for upgrade_version, upgrade_path in UPGRADE_PATHS.items():
        if upgrade_version > last_upgrade:
            upgrade_string = str(upgrade_version)
            echo(f"Running OSM upgrade: v{upgrade_string} ", nl=False)

            config = upgrade_path(config) # upgrade routines should accept and then return config,
                                          # in case it moves

            config["last_upgrade"] = upgrade_string
            config["version"] = upgrade_string
            config.store()
            echo("... done")
    echo("All OSM upgrades applied. ", nl=False)
    return config

def _upgrade_0_0_10a3(config:JsonStorageXDG=None):
    """Upgrade early alphas to v0.0.10a3

        Migrates config file from JsonStorageXDG to JsonConfigXDG,
        and changes the subdirectory to OpenVoiceOS, resulting in
        the path `~/.config/OpenVoiceOS/OVOS-SkillsManager.json`
    """
    if isinstance(config, JsonConfigXDG):
        # This upgrade's only purpose is to migrate config from JsonStorageXDG to
        # JsonConfigXDG. We have arrived here in error. Goodbye.
        return config

    # Migrate config file
    old_config = config or JsonStorageXDG("OVOS-SkillsManager")
    if path.exists(old_config.path):
        new_config = \
            JsonConfigXDG("OVOS-SkillsManager",
                            subfolder="OpenVoiceOS").merge(old_config,
                                                    skip_empty=False)
        new_config.store()
        remove(old_config.path)
        return new_config
    raise FileNotFoundError("Unable to execute OSM upgrade 0.0.9 --> 0.0.10a3: "
                            "could not find old config")


UPGRADE_PATHS = OrderedDict({
    # Each version with an upgrade should map to a function, which should accept and return config
    version.parse("0.0.10a3"): _upgrade_0_0_10a3
})
