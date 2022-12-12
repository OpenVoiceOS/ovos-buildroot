from ovos_skills_manager.skill_entry import SkillEntry
from ovos_config.config import Configuration
from ovos_skills_manager.session import SESSION as requests
from ovos_skills_manager.github.raw import is_valid_github_skill_url, \
    validate_branch, normalize_github_url
from ovos_skills_manager.exceptions import GithubInvalidBranch
from ovos_skills_manager.appstores import AbstractAppstore
from ovos_utils.log import LOG


def get_current_marketplace_branch():
    # TODO check mycroft version for default branch as fallback
    try:
        default_branch = Configuration().get("skills", {}) \
            .get("msm", {}).get("repo", {}).get("branch", "21.02")
    except FileNotFoundError:
        default_branch = "21.02"
    return default_branch


def get_marketplace_json(branch=None):
    branch = branch or get_current_marketplace_branch()
    url = "https://raw.githubusercontent.com/MycroftAI/mycroft-skills-data/{branch}/skill-metadata.json".format(branch=branch)
    r = requests.get(url)
    if not r.status_code == 200:
        raise GithubInvalidBranch
    return r.json()


def get_mycroft_marketplace_skill_urls(branch=None):
    data = get_marketplace_json(branch)
    for _, skill in data.items():
        yield skill["repo"] + "/tree/" + skill["tree"]


def get_mycroft_marketplace_skill_urls_from_submodules(branch=None):
    branch = branch or get_current_marketplace_branch()
    url = "https://raw.githubusercontent.com/MycroftAI/mycroft-skills/{branch}/.gitmodules".format(branch=branch)
    r = requests.get(url)
    if not r.status_code == 200:
        raise GithubInvalidBranch
    for l in r.text.split("[submodule "):
        if not l:
            continue
        yield l.split("url = ")[-1].strip()


def get_mycroft_marketplace_skills(branch:str=None, parse_github:bool=False,
                                   skiplist=None):
    skiplist = skiplist or []
    data = get_marketplace_json(branch)
    for _, skill in data.items():
        url = skill["repo"]
        branch = skill["tree"]
        if normalize_github_url(url) in skiplist:
            continue
        data = {
            "skillname": skill["display_name"],
            "foldername": skill["name"],
            "url": url,
            "branch": branch,
            "description": skill["description"],
            "authorname": skill["github_username"],
            "examples": skill["examples"],
            "category": skill["categories"][0],
            "tags": list(set(skill["tags"] + skill["categories"])),
            "platforms": skill["platforms"],
            "short_description": skill["short_desc"]
        }
        if parse_github:
            try:
                validate_branch(branch, url)
            except GithubInvalidBranch:
                LOG.error("branch : {branch} not available for skill: {skill}".format(branch=branch, skill=url))
                continue
            if not is_valid_github_skill_url(url, branch):
                LOG.error("{skill} does not seem like a valid skill".format(skill=url))
                continue

        yield SkillEntry.from_json(data, parse_github=parse_github)


class MycroftMarketplace(AbstractAppstore):
    def __init__(self, *args, **kwargs):
        super().__init__("MycroftMarketplace",
                         appstore_id="mycroft_marketplace", *args, **kwargs)

    def get_skills_list(self, skiplist=None):
        return get_mycroft_marketplace_skills(
            parse_github=self.parse_github, skiplist=skiplist)
