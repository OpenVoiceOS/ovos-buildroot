from ovos_skills_manager.skill_entry import SkillEntry
from ovos_skills_manager.appstores import AbstractAppstore
from ovos_skills_manager.session import SESSION as requests
from ovos_skills_manager.exceptions import AuthenticationError
import base64
import json


def get_neon_skills_from_api(parse_github:bool=False, skiplist=None):
    skiplist = skiplist or []
    skills_url = "https://api.github.com/repos/NeonGeckoCom/neon-skills-submodules/contents/skill-metadata.json"
    skill_json = requests.get(skills_url).json()
    if skill_json.get("message") == 'Not Found' or "API rate limit exceeded" \
            in skill_json.get("message", ""):
        raise AuthenticationError

    if skill_json.get("encoding") == "base64":
        json_str = base64.b64decode(skill_json["content"]).decode("utf-8")
        skill_json = json.loads(json_str)

    for skill in skill_json.values():
        if skill["url"] in skiplist:
            continue
        skill["appstore"] = "Neon"
        skill["appstore_url"] = skills_url
        yield SkillEntry.from_json(skill,
                                   parse_github=parse_github)


def get_neon_skills(parse_github:bool=False, skiplist=None):
    skiplist = skiplist or []
    skills_url = "https://raw.githubusercontent.com/NeonGeckoCom/neon-skills-submodules/master/skill-metadata.json"
    skill_json = requests.get(skills_url).json()
    for skill in skill_json.values():
        if skill["url"] in skiplist:
            continue
        skill["appstore"] = "Neon"
        skill["appstore_url"] = skills_url
        yield SkillEntry.from_json(skill,
                                   parse_github=parse_github)


class NeonSkills(AbstractAppstore):
    def __init__(self, *args, **kwargs):
        super().__init__("Neon", appstore_id="neon", *args, **kwargs)

    def get_skills_list(self, skiplist=None):
        skiplist = skiplist or []
        return get_neon_skills(parse_github=self.parse_github,
                               skiplist=skiplist)
