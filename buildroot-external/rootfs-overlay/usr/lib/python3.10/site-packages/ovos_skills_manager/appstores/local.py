from os import listdir
from os.path import join, isdir
from typing import Optional

from ovos_utils.skills import get_skills_folder

from ovos_skills_manager.local_skill import get_skill_data_from_directory
from ovos_skills_manager.skill_entry import SkillEntry
from ovos_skills_manager.appstores import AbstractAppstore


def get_local_skills(parse_github: bool = False,
                     skiplist: Optional[list] = None):
    try:
        skills = get_skills_folder()
    except FileNotFoundError:
        return
    except KeyError:
        # TODO: Patching config error in ovos_utils
        return
    skiplist = skiplist or []
    folders = listdir(skills)
    for fold in folders:
        path = join(skills, fold)
        if not isdir(path) or fold in skiplist:
            continue

        skill_dir = join(skills, fold)
        skill = get_skill_data_from_directory(skill_dir)
        yield SkillEntry.from_json(skill, parse_github=parse_github)


class InstalledSkills(AbstractAppstore):
    def __init__(self, *args, **kwargs):
        super().__init__("InstalledSkills", appstore_id="local",
                         *args, **kwargs)

    def get_skills_list(self, skiplist=None):
        skiplist = skiplist or []
        return get_local_skills(parse_github=self.parse_github,
                                skiplist=skiplist)
