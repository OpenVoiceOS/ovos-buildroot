from ovos_plugin_manager.utils import find_plugins, PluginTypes
from ovos_utils.log import LOG


def find_skill_plugins():
    return find_plugins(PluginTypes.SKILL)


def load_skill_plugins(*args, **kwargs):
    """Load installed skill plugins.

    Returns:
        List of skills
    """
    plugin_skills = []
    plugins = find_skill_plugins()
    for skill_id, plug in plugins.items():
        try:
            skill = plug(*args, **kwargs)
        except:
            LOG.exception(f"Failed to load {skill_id}")
            continue
        plugin_skills.append(skill)
    return plugin_skills
