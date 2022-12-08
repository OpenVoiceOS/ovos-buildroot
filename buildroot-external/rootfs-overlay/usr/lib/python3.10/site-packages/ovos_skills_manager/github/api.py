from ovos_utils.log import LOG
from ovos_utils.json_helper import merge_dict
from ovos_skills_manager.github.utils import author_repo_from_github_url, \
    get_branch_from_github_url, skill_name_from_github_url, blob2raw, \
    GITHUB_README_FILES, GITHUB_ANDROID_FILES, GITHUB_LOGO_FILES, \
    GITHUB_ICON_FILES, GITHUB_JSON_FILES, GITHUB_DESKTOP_FILES, \
    GITHUB_MANIFEST_FILES, GITHUB_LICENSE_FILES, \
    GITHUB_SKILL_REQUIREMENTS_FILES, GITHUB_REQUIREMENTS_FILES, GithubUrls
from ovos_skills_manager.exceptions import *
from ovos_skills_manager.licenses import parse_license_type, is_viral, \
    is_permissive
from ovos_skills_manager.utils import desktop_to_json, readme_to_json
from ovos_skills_manager.requirements import validate_manifest
from ovos_skills_manager.session import SESSION as requests
import base64
import json
from enum import Enum
from typing import Optional


# TODO github api token from env

class GithubAPI(str, Enum):
    BASE = "https://api.github.com"
    LICENSE_LIST = BASE + "/licenses"
    LICENSE_DATA = LICENSE_LIST + "/{license_type}"
    REPO = BASE + "/repos/{owner}/{repo}"
    REPO_LICENSE = REPO + "/license"
    REPO_README = REPO + "/readme"
    REPO_RELEASES = REPO + "/tags"
    REPO_FILE = REPO + '/contents/{file}'
    REPO_ZIP = REPO + '/zipball/{branch}'


def api_zip_url_from_github_url(url: str, branch: Optional[str] = None,
                                token: Optional[str] = None) -> str:
    """
    Get an API URL to download the repository as a zip archive
    https://docs.github.com/en/rest/reference/repos#download-a-repository-archive-zip
    @param url: Repository URL, optionally containing a branch spec
    @param branch: Optional branch spec, otherwise branch from `url` will be used
    @param token: Optional GitHub token to include with request
    @return: GitHub API URL to query for a zip archive
    """
    # TODO: `token` is not used?
    # specific file
    try:
        url = blob2raw(url)
        if requests.get(url).ok:
            return url
    except GithubInvalidUrl:
        pass

    # full git repo
    branch = branch or get_branch_from_github_url(url)
    owner, repo = author_repo_from_github_url(url)
    url = GithubAPI.REPO_ZIP.format(owner=owner, branch=branch, repo=repo)
    if requests.get(url).status_code == 200:
        return url

    raise GithubInvalidUrl


# Github API methods
def get_repo_data_from_github_api(url: str,
                                  branch: Optional[str] = None) -> dict:
    """
    Get git data for the repository at the given URL and branch
    https://docs.github.com/en/rest/reference/repos#get-a-repository
    @param url: Repository URL
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: dict repository data
    """
    # TODO: Handle branch spec in URL?
    author, repo = author_repo_from_github_url(url)
    url = GithubAPI.REPO.format(owner=author, repo=repo)
    try:
        resp = requests.get(url, params={"ref": branch})
        data = resp.json()
    except Exception as e:
        raise GithubAPIRepoNotFound(e)
    if "API rate limit exceeded" in data.get("message", ""):
        raise GithubAPIRateLimited(data.get("message"))
    if not resp.ok:
        raise GithubAPIException(resp.status_code)
    return data


def get_license_data_from_github_api(url: str,
                                     branch: Optional[str] = None) -> dict:
    """
    Get license data for the repository at the given URL and branch
    https://docs.github.com/en/rest/reference/licenses#get-the-license-for-a-repository
    @param url: Repository URL
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: dict license data
    """
    author, repo = author_repo_from_github_url(url)
    url = GithubAPI.REPO_LICENSE.format(owner=author, repo=repo)
    try:
        data = requests.get(url, params={"ref": branch}).json()
    except Exception as e:
        raise GithubAPILicenseNotFound
    if "API rate limit exceeded" in data.get("message", ""):
        raise GithubAPIRateLimited
    return data


def get_repo_releases_from_github_api(url: str,
                                      branch: Optional[str] = None) -> list:
    """
    Get releases data for the repository at the specified URL and branch
    https://docs.github.com/en/rest/reference/repos#list-repository-tags
    @param url: Repository URL
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: repo tag data
    """
    # TODO: There is a releases API, but this uses the tags API
    try:
        author, repo = author_repo_from_github_url(url)
        url = GithubAPI.REPO_RELEASES.format(owner=author, repo=repo)
        data = requests.get(url, params={"ref": branch}).json()
    except Exception as e:
        raise GithubAPIReleasesNotFound(str(e))
    if isinstance(data, dict):
        # result is usually a list, unless api call fails
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
    # let's fix api urls
    for idx, r in enumerate(data):
        data[idx]["tarball_url"] = GithubUrls.DOWNLOAD_TARBALL.format(
            author=author, repo=repo, branch=r["name"])
        data[idx]["zipball_url"] = GithubUrls.DOWNLOAD.format(
            author=author, repo=repo, branch=r["name"])
        data[idx].pop('node_id')
    return data


# url getters
def get_license_url_from_github_api(url: str,
                                    branch: str = None) -> str:
    """
    Try to get a license file url for the repository at the given url and branch
    @param url: Repository URL
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: url to be used for downloading the repository license file
    """
    try:
        data = get_license_data_from_github_api(url, branch)
        return data["download_url"]
    except GithubAPILicenseNotFound:
        pass
    for dst in GITHUB_LICENSE_FILES:
        try:
            data = get_file_from_github_api(url, dst, branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("download_url"):
            return data["download_url"]
    raise GithubAPILicenseNotFound


# data getters
def get_main_branch_from_github_api(url: str, branch: str = None) -> str:
    """
    Determine the preferred branch for the specified URL.
    @param url: Repository URL
    @param branch: Optional branch spec to read skill.json from,
    otherwise default branch will be used
    @return: default branch name read from skill.json or latest release
    """
    try:
        # implicit in url
        return get_branch_from_github_url(url)
    except GithubInvalidBranch:
        pass
    try:
        data = get_repo_data_from_github_api(url, branch)
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        return data.get('default_branch') or branch
    except GithubAPIRateLimited:
        raise
    except Exception as e:
        raise GithubAPIInvalidBranch(str(e))


def get_latest_release_from_api(url: str) -> dict:
    """
    Determine the main branch for the specified URL.
    https://docs.github.com/en/rest/reference/repos#list-repository-tags
    @param url: Repository URL
    @return: data associated with latest tagged release
    """
    # TODO: API returns dict but raw returns str?
    return get_repo_releases_from_github_api(url)[0]


def get_branch_from_latest_release_github_api(url: str) -> str:
    """
    Determine the branch associated with the latest GitHub Release if specified
    @param url: Repository URL
    @return: branch spec of latest tag
    """
    try:
        return get_latest_release_from_api(url)["name"]
    except IndexError:
        raise GithubInvalidBranch(f"no releases for {url}")
    except Exception as e:
        raise GithubAPIRateLimited


def get_file_from_github_api(url: str, filepath: str,
                             branch: Optional[str] = None) -> dict:
    """
    Get information for a file in a repository.
    https://docs.github.com/en/rest/reference/repos#get-repository-content
    @param url: Repository URL
    @param filepath: path to a file in the repository
    @param branch: Optional branch to query, otherwise branch from `url` will be used
    @return: parsed API data
    """
    author, repo = author_repo_from_github_url(url)
    branch = branch or get_main_branch_from_github_api(url)
    url = GithubAPI.REPO_FILE.format(owner=author, repo=repo, file=filepath)
    resp = requests.get(url, params={"ref": branch})
    data = resp.json()
    if "API rate limit exceeded" in data.get("message", ""):
        raise GithubAPIRateLimited
    if "Bad credentials" in data.get("message", ""):
        LOG.info(requests.headers)
        raise GithubAPIException(data)
    if resp.ok:
        return data
    raise GithubAPIFileNotFound(f"{resp.url} returned {resp.status_code}:"
                                f" {resp.content}")


def get_readme_url_from_github_api(url: str,
                                   branch: Optional[str] = None) -> str:
    """
    Get the readme file url for the specified repository
    https://docs.github.com/en/rest/reference/repos#get-a-repository-readme
    @param url: Repository URL
    @param branch: Optional branch to query, otherwise default branch will be used
    @return: url of repository README file
    """
    author, repo = author_repo_from_github_url(url)
    default_url = GithubAPI.REPO_README.format(owner=author, repo=repo)
    try:
        data = requests.get(default_url, params={"ref": branch}).json()
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        return data["html_url"]
    except Exception as e:
        pass  # check files individually

    for dst in GITHUB_README_FILES:
        try:
            data = get_file_from_github_api(url, dst, branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("html_url"):
            return data["html_url"]
    raise GithubAPIReadmeNotFound


def get_readme_from_github_api(url: str,
                               branch: Optional[str] = None) -> str:
    """
    Get the readme file contents for the specified repository
    @param url: Repository URL
    @param branch: Optional branch to query, otherwise default branch will be used
    @return: contents of repository README file
    """
    author, repo = author_repo_from_github_url(url)
    default_url = GithubAPI.REPO_README.format(owner=author, repo=repo)
    try:
        data = requests.get(default_url, params={"ref": branch}).json()
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        readme = data["content"]
        if data["encoding"] == "base64":
            return base64.b64decode(readme).decode("utf-8")
        # TODO Raise UnknownEncoding?
        return readme
    except GithubAPIRateLimited:
        raise
    except Exception as e:
        pass

    # check files individually
    for dst in GITHUB_README_FILES:
        try:
            data = get_file_from_github_api(url, dst, branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        readme = data.get("content")
        if readme:
            if data["encoding"] == "base64":
                return base64.b64decode(readme).decode("utf-8")
            # TODO Raise UnknownEncoding?
            return readme
    raise GithubAPIReadmeNotFound


def get_license_type_from_github_api(url: str,
                                     branch: Optional[str] = None) -> str:
    """
    Determine the License Name for the license of a given repository
    https://docs.github.com/en/rest/reference/licenses#get-the-license-for-a-repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: License Name
    """
    try:
        data = get_repo_data_from_github_api(url, branch)
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        return data["license"]["key"]
    except Exception as e:
        pass
    text = get_license_from_github_api(url, branch)
    return parse_license_type(text)


def get_license_from_github_api(url: str, branch: str = None) -> str:
    """
    Get string contents of the license file for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: License file contents
    """
    try:
        data = get_license_data_from_github_api(url, branch)
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("content"):
            text = data["content"]
            if data["encoding"] == "base64":
                return base64.b64decode(text).decode("utf-8")
            return text
    except Exception as e:
        pass
    for dst in GITHUB_LICENSE_FILES:
        data = get_file_from_github_api(url, dst, branch)
        if data.get("content"):
            text = data["content"]
            if data["encoding"] == "base64":
                return base64.b64decode(text).decode("utf-8")
            # TODO Raise UnknownEncoding?
            return text
    raise GithubAPILicenseNotFound


def get_requirements_from_github_api(url: str,
                                     branch: Optional[str] = None) -> list:
    """
    Get Python requirements from text files in the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: List parsed python requirements
    """
    author, repo = author_repo_from_github_url(url)
    content = None
    for dst in GITHUB_REQUIREMENTS_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue

        if data.get("content"):
            content = data["content"]
            if data["encoding"] == "base64":
                content = base64.b64decode(content).decode("utf-8")
            # TODO Raise UnknownEncoding?
    if not content:
        raise GithubAPIFileNotFound
    return [t for t in content.split("\n")
            if t.strip() and not t.strip().startswith("#")]


def get_skill_requirements_from_github_api(url: str,
                                           branch: Optional[str] = None) -> list:
    """
    Get Skill requirements from text files in the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: List parsed skill requirements
    """
    author, repo = author_repo_from_github_url(url)
    content = None
    for dst in GITHUB_SKILL_REQUIREMENTS_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited(data.get("message"))
        if data.get("content"):
            content = data["content"]
            if data["encoding"] == "base64":
                content = base64.b64decode(content).decode("utf-8")
            # TODO Raise UnknownEncoding?
    if not content:
        raise GithubAPIFileNotFound("Requirements file not found")
    return [t for t in content.split("\n")
            if t.strip() and not t.strip().startswith("#")]


def get_manifest_from_github_api(url: str,
                                 branch: Optional[str] = None) -> dict:
    """
    Get requirements specified in the repository manifest file
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: dict parsed requirements
    """
    author, repo = author_repo_from_github_url(url)
    content = None
    for dst in GITHUB_MANIFEST_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("content"):
            content = data["content"]
            if data["encoding"] == "base64":
                content = base64.b64decode(content).decode("utf-8")
            # TODO Raise UnknownEncoding?
    if not content:
        raise GithubAPIFileNotFound
    return validate_manifest(content)


def get_json_url_from_github_api(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get skill.json file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill.json
    """
    author, repo = author_repo_from_github_url(url)
    for dst in GITHUB_JSON_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("html_url"):
            return data["html_url"]
    raise GithubAPIFileNotFound


def get_skill_json_from_github_api(url: str,
                                   branch: Optional[str] = None) -> dict:
    """
    Get skill.json file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: data parsed from skill.json
    """
    author, repo = author_repo_from_github_url(url)
    for dst in GITHUB_JSON_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("content"):
            content = data["content"]
            if data["encoding"] == "base64":
                json_data = base64.b64decode(content).decode("utf-8")
            else:
                # TODO Raise UnknownEncoding?
                json_data = content
            return json.loads(json_data)
    raise GithubAPIFileNotFound


def get_desktop_url_from_github_api(url: str,
                                    branch: Optional[str] = None) -> str:
    """
    Get skill.desktop file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill.desktop
    """
    author, repo = author_repo_from_github_url(url)
    for dst in GITHUB_DESKTOP_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("html_url"):
            return data["html_url"]
    raise GithubAPIFileNotFound


def get_desktop_from_github_api(url: str,
                                branch: Optional[str] = None) -> str:
    """
    Get skill.desktop file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: skill.desktop string contents
    """
    author, repo = author_repo_from_github_url(url)
    for dst in GITHUB_DESKTOP_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("content"):
            readme = data["content"]
            if data["encoding"] == "base64":
                return base64.b64decode(readme).decode("utf-8")
            # TODO Raise UnknownEncoding?
            return readme
    raise GithubAPIFileNotFound


def get_desktop_json_from_github_api(url: str,
                                     branch: Optional[str] = None) -> dict:
    """
    Get parsed skill.desktop file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: skill.desktop contents parsed into a dict
    """
    desktop = get_desktop_from_github_api(url, branch)
    return desktop_to_json(desktop)


# data parsers
def get_readme_json_from_api(url: str, branch: Optional[str] = None) -> dict:
    """
    Get parsed readme file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: Readme contents parsed into a dict
    """
    readme = get_readme_from_github_api(url, branch)
    return readme_to_json(readme)


def get_requirements_json_from_github_api(url: str,
                                          branch: Optional[str] = None) -> dict:
    """
    Get parsed requirements for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: requirements with keys: {python, system, skill}
    """
    data = {"python": [], "system": {}, "skill": []}
    try:
        manif = get_manifest_from_github_api(url, branch)
        data = manif['dependencies'] or {"python": [], "system": {},
                                         "skill": []}
    except GithubAPIFileNotFound:
        pass
    try:
        req = get_requirements_from_github_api(url, branch)
        data["python"] = list(set(data["python"] + req))
    except GithubAPIFileNotFound:
        pass
    try:
        skill_req = get_skill_requirements_from_github_api(url, branch)
        data["skill"] = list(set(data["skill"] + skill_req))
    except GithubAPIFileNotFound:
        pass
    return data


def get_branch_from_skill_json_github_api(url: str,
                                          branch: Optional[str] = None):
    """
    Get branch specified in skill.json file for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: branch spec from skill.json or `branch`
    """
    try:
        json_data = get_skill_json_from_github_api(url, branch)
        return json_data.get("branch") or branch
    except GithubAPIFileNotFound:
        return branch


def get_skill_from_api(url: str,
                       branch: Optional[str] = None,
                       strict: bool = False) -> dict:
    """
    Parse serialized `SkillEntry` data from the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @param strict: If true, requires a release to be specified, even if branch passed
    @return: data to build a `SkillEntry`
    """
    data = {}

    # extract branch from .json, should branch take precedence?
    # i think so because user explicitly requested it
    branch = get_branch_from_skill_json_github_api(url, branch)

    try:
        api_data = get_repo_data_from_github_api(url, branch)
        data["branch"] = branch = api_data['default_branch']
        data["short_description"] = api_data['description']
        data["license"] = api_data["license"]["key"]
        data["foldername"] = api_data["name"]
        data["last_updated"] = api_data['updated_at']
        data["url"] = api_data["html_url"]
        data["authorname"] = api_data["owner"]["login"]
    except GithubAPIException:
        LOG.error("Failed to retrieve repo data from github api")
        raise

    try:
        releases = get_repo_releases_from_github_api(url, branch)
        if branch:
            for r in releases:
                if r["name"] == branch or r["commit"]["sha"] == branch:
                    data["version"] = r["name"]
                    # data["download_url"] = r["tarball_url"]
                    break
        else:
            data["version"] = releases[0]["name"]
            # data["download_url"] = releases[0]["tarball_url"]
    except GithubAPIException:
        LOG.error("Failed to retrieve releases data from github api")
        if strict:
            # TODO: Should this really happen if we spec'd a branch?
            raise GithubAPIReleasesNotFound

    # augment with readme data
    try:
        data = merge_dict(data, get_readme_json_from_api(url, branch),
                          merge_lists=True, skip_empty=True, no_dupes=True)
    except GithubAPIReadmeNotFound:
        pass

    data["requirements"] = get_requirements_json_from_github_api(url, branch)

    # find logo
    try:
        data["logo"] = get_logo_url_from_github_api(url, branch)
    except GithubAPIFileNotFound as e:
        pass

    # find icon
    try:
        data["icon"] = icon = get_icon_url_from_github_api(url, branch)
    except GithubAPIFileNotFound:
        icon = None

    # augment with android data
    try:
        data["android"] = get_android_json_from_github_api(url, branch)
    except GithubAPIFileNotFound:
        # best guess or throw exception?
        author, repo = author_repo_from_github_url(url)
        data["android"] = {
            'android_icon': icon,
            'android_name': skill_name_from_github_url(url),
            'android_handler': '{repo}.{author}.home'.format(repo=repo,
                                                             author=author.lower())}

    # augment with desktop data
    try:
        data["desktop"] = get_desktop_json_from_github_api(url, branch)
        data["desktopFile"] = True
    except GithubFileNotFound:
        data["desktopFile"] = False

    # augment tags
    if "tags" not in data:
        data["tags"] = []
    if is_viral(data["license"]):
        data["tags"].append("viral-license")
    elif is_permissive(data["license"]):
        data["tags"].append("permissive-license")
    elif "unknown" in data["license"]:
        data["tags"].append("no-license")

    # augment with json data
    # this should take precedence over everything else
    try:
        data = merge_dict(data, get_skill_json_from_github_api(url, branch),
                          merge_lists=True, skip_empty=True, no_dupes=True)
    except GithubFileNotFound:
        pass

    return data


def get_icon_url_from_github_api(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get skill icon file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill icon
    """
    author, repo = author_repo_from_github_url(url)
    for dst in GITHUB_ICON_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("download_url"):
            return data["download_url"]
    raise GithubAPIFileNotFound


def get_logo_url_from_github_api(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get skill logo file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill logo
    """
    author, repo = author_repo_from_github_url(url)
    for dst in GITHUB_LOGO_FILES:
        try:
            data = get_file_from_github_api(url, dst.format(repo=repo), branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("download_url"):
            return data["download_url"]
    raise GithubAPIFileNotFound


def get_android_url_from_github_api(url: str,
                                    branch: Optional[str] = None) -> str:
    """
    Get android.json file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of android.json
    """
    for dst in GITHUB_ANDROID_FILES:
        try:
            data = get_file_from_github_api(url, dst, branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("download_url"):
            return data["download_url"]
    raise GithubAPIFileNotFound


def get_android_json_from_github_api(url: str,
                                     branch: Optional[str] = None) -> dict:
    """
    Get parsed android.json file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: parsed android.json contents
    """
    for dst in GITHUB_ANDROID_FILES:
        try:
            data = get_file_from_github_api(url, dst, branch)
        except GithubAPIFileNotFound:
            continue
        if "API rate limit exceeded" in data.get("message", ""):
            raise GithubAPIRateLimited
        if data.get("content"):
            android = data["content"]
            if data["encoding"] == "base64":
                return json.loads(base64.b64decode(android).decode("utf-8"))
            # TODO Raise UnknownEncoding?
            return android
    raise GithubAPIFileNotFound
