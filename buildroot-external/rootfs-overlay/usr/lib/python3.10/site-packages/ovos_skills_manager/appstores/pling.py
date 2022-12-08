from ovos_skills_manager.session import SESSION as requests
from ovos_utils.xml_helper import xml2dict
from ovos_skills_manager.skill_entry import SkillEntry
from ovos_skills_manager.exceptions import JSONDecodeError
from ovos_skills_manager.appstores import AbstractAppstore
import json
from ovos_utils.log import LOG


def _parse_pling(skill):
    if isinstance(skill, str):
        json_data = json.loads(skill)
    else:
        json_data = skill

    # TODO is it a safe assumption downloadlink1 is always the skill.json ?
    # this can be made smarter
    url = json_data["downloadlink1"]
    try:
        skill_json = requests.get(url).json()
    except JSONDecodeError:
        return {}

    # rename
    skill_json["skillname"] = skill_json.pop("name")

    # save useful data to skill.meta_info
    skill_json["logo"] = json_data["previewpic1"]
    skill_json["category"] = json_data['typename']
    skill_json["created"] = json_data['created']
    skill_json["modified"] = json_data['changed']
    skill_json["description"] = json_data["description"]
    skill_json["tags"] = json_data['tags'].split(",")
    skill_json["authorname"] = json_data['personid']
    skill_json["version"] = json_data["version"]

    # appstore data
    # TODO also provide this from mycroft appstore
    skill_json["appstore"] = "pling.opendesktop"
    skill_json["appstore_url"] = json_data["detailpage"]

    return skill_json


def get_pling_skills(parse_github:bool=False, skiplist=None):
    skiplist = skiplist or []
    url = "https://api.kde-look.org/ocs/v1/content/data"
    params = {"categories": "608", "page": 0}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        LOG.error(f"could not reach pling! status code: {r.status_code}")
        return
    data = xml2dict(r.text)
    meta = data["ocs"]["meta"]
    n_pages = int(meta["totalitems"]) // int(meta["itemsperpage"])

    for n in range(0, n_pages + 1):
        LOG.debug("Parsing pling page {i} out of {n}".format(i=n, n=n_pages))
        params = {"categories": "608", "page": n}
        xml = requests.get(url, params=params).text
        for skill in xml2dict(xml)["ocs"]["data"]["content"]:
            skill_json = _parse_pling(skill)
            if skill_json.get("url", "") in skiplist or not skill_json.get("url"):
                continue
            yield SkillEntry.from_json(skill_json, parse_github=parse_github)


class Pling(AbstractAppstore):
    def __init__(self, *args, **kwargs):
        super().__init__("Pling", appstore_id="pling", *args, **kwargs)

    def get_skills_list(self, skiplist=None):
        skiplist = skiplist or []
        return get_pling_skills(parse_github=self.parse_github,
                                skiplist=skiplist)
