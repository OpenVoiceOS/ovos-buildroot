from ovos_config.config import read_mycroft_config, update_mycroft_config
from ovos_utils.messagebus import wait_for_reply
from ovos_utils.skills.locations import get_default_skills_directory, get_installed_skill_ids
from ovos_utils.log import LOG


def get_non_properties(obj):
    """Get attributes that are not properties from object.

    Will return members of object class along with bases down to MycroftSkill.

    Args:
        obj: object to scan

    Returns:
        Set of attributes that are not a property.
    """

    def check_class(cls):
        """Find all non-properties in a class."""
        # Current class
        d = cls.__dict__
        np = [k for k in d if not isinstance(d[k], property)]
        # Recurse through base classes excluding MycroftSkill and object
        for b in [b for b in cls.__bases__ if b.__name__ not in ("object", "MycroftSkill")]:
            np += check_class(b)
        return np

    return set(check_class(obj.__class__))


def skills_loaded(bus=None):
    reply = wait_for_reply('mycroft.skills.all_loaded',
                           'mycroft.skills.all_loaded.response',
                           bus=bus)
    if reply:
        return reply.data['status']
    return False


def blacklist_skill(skill, config=None):
    config = config or read_mycroft_config()
    skills_config = config.get("skills", {})
    blacklisted_skills = skills_config.get("blacklisted_skills", [])
    if skill not in blacklisted_skills:
        blacklisted_skills.append(skill)
        conf = {
            "skills": {
                "blacklisted_skills": blacklisted_skills
            }
        }
        update_mycroft_config(conf)
        return True
    return False


def whitelist_skill(skill, config=None):
    config = config or read_mycroft_config()
    skills_config = config.get("skills", {})
    blacklisted_skills = skills_config.get("blacklisted_skills", [])
    if skill in blacklisted_skills:
        blacklisted_skills.pop(skill)
        conf = {
            "skills": {
                "blacklisted_skills": blacklisted_skills
            }
        }
        update_mycroft_config(conf)
        return True
    return False


def make_priority_skill(skill, config=None):
    config = config or read_mycroft_config()
    skills_config = config.get("skills", {})
    priority_skills = skills_config.get("priority_skills", [])
    if skill not in priority_skills:
        priority_skills.append(skill)
        conf = {
            "skills": {
                "priority_skills": priority_skills
            }
        }
        update_mycroft_config(conf)
        return True
    return False


def get_skills_folder(config=None):
    LOG.warning("This reference is deprecated, use "
                "`ovos_utils.skills.locations.get_default_skill_dir")
    return get_default_skills_directory(config)


def get_installed_skills(config=None):
    LOG.warning("This reference is deprecated, use "
                "`ovos_utils.skills.locations.get_installed_skill_ids")
    return get_installed_skill_ids(config)
