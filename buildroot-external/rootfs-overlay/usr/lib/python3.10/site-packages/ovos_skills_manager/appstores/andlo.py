from ovos_skills_manager.session import SESSION as requests
from ovos_skills_manager import SkillEntry
from ovos_skills_manager.appstores import AbstractAppstore
from ovos_skills_manager.exceptions import GithubInvalidUrl
from ovos_utils.log import LOG


def get_andlos_list_skills(parse_github:bool=False, skiplist=None):
    skiplist = skiplist or []
    url = "https://raw.githubusercontent.com/andlo/mycroft-skills-list-gitbook/master/_data/skills.json"
    andlos_list = requests.get(url).json()
    for idx, skill in enumerate(andlos_list):
        LOG.debug("Parsing skill {i} out of {n}".format(i=idx,
                                                        n=len(andlos_list)))
        s = skill['skill_info']
        if s['repo'] in skiplist:
            continue
        cats = [s for s in s['categories'] if len(s) > 2]
        cat = cats[0] if len(cats) else None
        tags = list(set(s['tags'] + cats))
        license = skill.get('license') or {}
        data = {
            "created": skill['created_at'],
            'archived': skill['archived'],
            "license": license.get("key"),
            'modified': skill['updated_at'],
            "authorname": s['github_username'],
            "skillname": s['name'],
            "foldername": s['id'],
            "name": s['name'],
            "url": s['repo'],
            'category': cat,
            "description": s['description'],
            "short_description": s['short_desc'],
            "branch": s['branch'],
            "examples": s['examples'],
            'tags': tags,
            'platforms': s['platforms'],
            'stars': skill['stargazers_count']
        }
        try:
            yield SkillEntry.from_json(data, parse_github)
        except GithubInvalidUrl:
            LOG.error("this skill does not seem to be valid! " + s['repo'])


class AndloSkillList(AbstractAppstore):
    def __init__(self, *args, **kwargs):
        super().__init__("AndloSkillList", appstore_id="andlo",
                         *args, **kwargs)

    def get_skills_list(self, skiplist=None):
        skiplist = skiplist or []
        return get_andlos_list_skills(parse_github=self.parse_github,
                                      skiplist=skiplist)
