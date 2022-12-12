from os.path import join, isdir, dirname, expanduser, isfile
from os import makedirs, listdir
from typing import List, Optional
from ovos_config.locations import get_xdg_data_save_path, get_xdg_data_dirs
from ovos_config.config import Configuration
from ovos_utils.log import LOG


def get_installed_skill_ids(conf: Optional[dict] = None) -> List[str]:
    """
    Gets a list of `skill_id`s for all installed skills
    Args:
        conf: Configuration, else loads from ovos_config.config.Configuration
    Returns:
        list of `skill_id` strings for all installed skills
    """
    _, skill_ids = get_plugin_skills()
    for d in get_skill_directories(conf):
        for skill_dir in listdir(d):
            if isdir(join(d, skill_dir)) and isfile(join(d, skill_dir,
                                                         "__init__.py")):
                if skill_dir in skill_ids:
                    LOG.info(f"{skill_dir} installed as plugin and local dir")
                    continue
                skill_ids.append(skill_dir)
    return skill_ids


def get_skill_directories(conf: Optional[dict] = None) -> List[str]:
    """ returns list of skill directories ordered by expected loading order
    This corresponds to:
    - XDG_DATA_DIRS
    - default directory (see get_default_skills_directory method for details)
    - user defined extra directories
    Each directory contains individual skill folders to be loaded
    If a skill exists in more than one directory (same folder name) previous instances will be ignored
        ie. directories at the end of the list have priority over earlier directories
    NOTE: empty folders are interpreted as disabled skills
    new directories can be defined in mycroft.conf by specifying a full path
    each extra directory is expected to contain individual skill folders to be loaded
    the xdg folder name can also be changed, it defaults to "skills"
        eg. ~/.local/share/mycroft/FOLDER_NAME
    {
        "skills": {
            "directory": "skills",
            "extra_directories": ["path/to/extra/dir/to/scan/for/skills"]
        }
    }
    Args:
        conf: Configuration, else loads from ovos_config.config.Configuration
    Returns:
        list of fully-qualified directories containing non-plugin skills
    """
    # the contents of each skills directory must be individual skill folders
    # we are still dependent on the mycroft-core structure of skill_id/__init__.py

    conf = conf or Configuration()

    # load all valid XDG paths
    # NOTE: skills are actually code, but treated as user data!
    # they should be considered applets rather than full applications
    skill_locations = list(reversed(
        [join(p, "skills") for p in get_xdg_data_dirs() if
         isdir(join(p, "skills"))]
    ))

    # load the default skills folder
    # only meaningful if xdg support is disabled
    default = get_default_skills_directory(conf)
    if default not in skill_locations:
        skill_locations.append(default)

    # load additional explicitly configured directories
    conf = conf.get("skills") or {}
    # extra_directories is a list of directories containing skill subdirectories
    # NOT a list of individual skill folders
    # preserve order while removing any duplicate entries
    extra_dirs = (expanduser(d) for d in conf.get("extra_directories") or [])
    for d in extra_dirs:
        if isdir(d) and d not in skill_locations:
            skill_locations.append(d)
    return skill_locations


def get_default_skills_directory(conf: Optional[dict] = None) -> str:
    """ return default directory to scan for skills
    This is only meaningful if xdg is disabled in ovos.conf
    If xdg is enabled then data_dir is always XDG_DATA_DIR
    If xdg is disabled then data_dir by default corresponds to /opt/mycroft
    users can define the data directory in mycroft.conf
    the skills folder name (relative to data_dir) can also be defined there
    NOTE: folder name also impacts all XDG skill directories!
    {
        "data_dir": "/opt/mycroft",
        "skills": {
            "directory": "skills"
        }
    }
    Args:
        conf: Configuration, else loads from ovos_config.config.Configuration
    Returns:
        Absolute path to default skills directory
    """
    conf = conf or Configuration()
    path_override = conf["skills"].get("directory_override")

    # if .conf wants to use a specific path, use it!
    if path_override:
        LOG.warning("'directory_override' is deprecated!\n"
                    "It will no longer be supported after version 0.0.3\n"
                    "add the new path to 'extra_directories' instead")
        skills_folder = expanduser(path_override)
    elif conf["skills"].get("extra_directories") and \
            len(conf["skills"].get("extra_directories")) > 0:
        skills_folder = expanduser(conf["skills"]["extra_directories"][0])
    else:
        skills_folder = join(get_xdg_data_save_path(), "skills")
    # create folder if needed
    try:
        makedirs(skills_folder, exist_ok=True)
    except PermissionError:  # old style /opt/mycroft/skills not available
        skills_folder = join(get_xdg_data_save_path(), "skills")
        makedirs(skills_folder, exist_ok=True)

    return skills_folder


def get_plugin_skills() -> (list, list):
    """
    Get the package directories for any pip installed skill plugins
    Returns:
        lists of skill directories and plugin skill IDs
    """
    import importlib.util
    try:
        from ovos_plugin_manager.skills import find_skill_plugins
    except ImportError:
        LOG.warning("ovos-plugin-manager not available to load plugin skills")
        return [], []
    skill_dirs = list()
    plugins = find_skill_plugins()
    skill_ids = list(plugins.keys())
    for skill_class in plugins.values():
        skill_dir = dirname(importlib.util.find_spec(
            skill_class.__module__).origin)
        skill_dirs.append(skill_dir)
    LOG.info(f"Located plugin skills: {skill_ids}")
    return skill_dirs, skill_ids
