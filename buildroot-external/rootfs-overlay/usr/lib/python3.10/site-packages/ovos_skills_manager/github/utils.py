from ovos_skills_manager.exceptions import *
from ovos_skills_manager.session import SESSION as requests
from ovos_utils import camel_case_split
from enum import Enum


class GithubUrls(str, Enum):
    URL = "https://github.com/{author}/{repo}"
    BRANCH = URL + "/tree/{branch}"
    BLOB = URL + "/blob/{branch}"
    README = BLOB + "/README.md"
    LICENSE = BLOB + "/LICENSE"
    SKILL_JSON = BLOB + "/skill.json"
    ANDROID_JSON = BLOB + "/android.json"
    DESKTOP_FILE = BLOB + "/res/desktop/{repo}.desktop"
    ICON = BLOB + "/res/icon/{icon}"
    LOGO = BLOB + "/ui/{logo}"
    SKILL = BLOB + "/__init__.py"
    MANIFEST = BLOB + "/manifest.yml"
    REQUIREMENTS = BLOB + "/requirements.txt"
    SKILL_REQUIREMENTS = BLOB + "/skill_requirements.txt"
    DOWNLOAD = URL + "/archive/{branch}.zip"
    DOWNLOAD_TARBALL = URL + "/archive/{branch}.tar.gz"
    TAGS = URL + "/tags"
    RELEASES = URL + "/releases"


GITHUB_README_FILES = ["README", "README.md", "README.txt", "README.rst",
                       "readme", "readme.md", "readme.rst", "readme.txt",
                       "Readme", "Readme.md", "Readme.rst", "Readme.txt"
                       ]

GITHUB_LICENSE_FILES = ["LICENSE", "LICENSE.txt", "UNLICENSE",
                        "LICENSE.md", "License", "License.md",
                        "License.txt", "license", "license.md", "license.txt"
                        ]

GITHUB_ICON_FILES = ["res/icon/{repo}", "res/icon/{repo}.png",
                     "res/icon/{repo}.svg", "res/icon/{repo}.jpg"]
GITHUB_JSON_FILES = ["skill.json", "res/desktop/skill.json",
                     "store/skill.json"]
GITHUB_ANDROID_FILES = ["android.json", "res/desktop/android.json"]
GITHUB_DESKTOP_FILES = ["res/desktop/{repo}.desktop", "{repo}.desktop"]
GITHUB_MANIFEST_FILES = ["manifest.yml"]
GITHUB_REQUIREMENTS_FILES = ["requirements.txt"]
GITHUB_SKILL_REQUIREMENTS_FILES = ["skill_requirements.txt"]
GITHUB_REQUIREMENTS_SCRIPT_FILES = ["requirements.sh"]
GITHUB_SKILL_INIT_FILES = ["__init__.py"]
GITHUB_LOGO_FILES = ["ui/logo.png", "logo.png",
                     "ui/{repo}.png", "ui/{repo}.svg", "ui/{repo}.jpg",
                     "store/{repo}.png", "store/{repo}.svg", "store/{repo}.jpg",
                     "{repo}.png",  "{repo}.svg", "{repo}.jpg"]


# url utils
def normalize_github_url(url):
    if "www.github.com" in url:
        url = url.replace("www.github.com", "github.com")

    url = url\
        .replace("git://", "https://")\
        .replace("https://raw.githubusercontent.com", "https://github.com")\
        .replace("https://api.github.com/repos/", "https://github.com/")\
        .replace(".git", "")
    if not url.startswith("https://github.com/"):
        raise GithubInvalidUrl(url)
    fields = url.replace("https://github.com/", "").split("/")
    author, skillname = fields[:2]
    if '@' in skillname:
        skillname = skillname.split('@')[0]
    return "/".join(["https://github.com", author, skillname])


def blob2raw(url:str, validate:bool=False):
    if not url.startswith("https://github.com") and \
            not url.startswith("https://raw.githubusercontent.com"):
        raise GithubInvalidUrl(url)
    url = url.replace("/blob", ""). \
        replace("https://github.com", "https://raw.githubusercontent.com")
    if validate:
        if requests.get(url).status_code != 200:
            raise GithubRawUrlNotFound(url)
    return url


def author_repo_from_github_url(url:str):
    url = normalize_github_url(url)
    return url.split("/")[-2:]


def skill_name_from_github_url(url:str):
    _, repo = author_repo_from_github_url(url)
    words = camel_case_split(repo.replace("-", " ").lower()).split(" ")
    name = " ".join([w for w in words if w != "skill"]) + " skill"
    return name.title()


def get_branch_from_github_url(url:str, validate:bool=False):
    branch = None
    url = url.replace("/blob/", "/tree/")
    if "/tree/" in url:
        branch = url.split("/tree/")[-1].split("/")[0]
    elif "/commit/" in url:
        branch = url.split("/commit/")[-1].split("/")[0]
    elif "/tag/" in url:
        branch = url.split("/tag/")[-1].split("/")[0]
    elif "@" in url:
        url, branch = url.split("@", 1)

    if branch:
        if validate:
            if not validate_branch(branch, url):
                raise GithubInvalidBranch
        return branch
    else:
        raise GithubInvalidBranch(branch)


def validate_branch(branch:str, url:str):
    url = normalize_github_url(url) + "/tree/{branch}".format(branch=branch)
    return requests.get(url).status_code == 200


def download_url_from_github_url(url: str, branch: str = None):
    # specific file
    try:
        url = blob2raw(url)
        if requests.get(url).status_code == 200:
            return url
    except GithubInvalidUrl:
        pass

    # full git repo
    branch = branch or get_branch_from_github_url(url)
    author, repo = author_repo_from_github_url(url)
    url = GithubUrls.DOWNLOAD.format(author=author, branch=branch, repo=repo)
    if requests.get(url).status_code == 200:
        return url

    raise GithubInvalidUrl(url)


def validate_github_skill_url(url:str, branch:str=None):
    branch = branch or get_branch_from_github_url(url)
    try:

        url = match_url_template(url, GithubUrls.SKILL, branch)
        data = requests.get(url).text

        if "def create_skill():" in data:
            return True
    except GithubInvalidUrl:
        pass
    raise GithubNotSkill


def is_valid_github_skill_url(url:str, branch:str=None):
    try:
        return validate_github_skill_url(url, branch)
    except Exception as e:
        return False


def match_url_template(url:str, template:str, branch:str=None):
    branch = branch or get_branch_from_github_url(url)
    author, repo = author_repo_from_github_url(url)
    url = template.format(author=author, branch=branch, repo=repo)
    if requests.get(url).status_code == 200:
        if "<title>Rate limit &middot; GitHub</title>" in requests.get(url).text:
            raise GithubHTTPRateLimited
        return blob2raw(url)
    raise GithubInvalidUrl(url)

