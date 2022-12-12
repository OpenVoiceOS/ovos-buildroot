from typing import Optional

from ovos_skills_manager.github.utils import *
from ovos_skills_manager.utils import desktop_to_json, readme_to_json
from ovos_skills_manager.licenses import parse_license_type, is_viral, \
    is_permissive
from ovos_utils.log import LOG
from ovos_utils.json_helper import merge_dict
import json
import yaml
import bs4
import base64


# Manual Extraction
GITHUB_README_LOCATIONS = [
    GithubUrls.BLOB + "/" + readme for readme in GITHUB_README_FILES
]

GITHUB_LICENSE_LOCATIONS = [
    GithubUrls.BLOB + "/" + lic for lic in GITHUB_LICENSE_FILES
]

GITHUB_ICON_LOCATIONS = [
    GithubUrls.BLOB + "/" + path for path in GITHUB_ICON_FILES
]

GITHUB_LOGO_LOCATIONS = [
    GithubUrls.BLOB + "/" + path for path in GITHUB_LOGO_FILES
]

GITHUB_JSON_LOCATIONS = [
    GithubUrls.BLOB + "/" + path for path in GITHUB_JSON_FILES
]

GITHUB_ANDROID_JSON_LOCATIONS = [
    GithubUrls.BLOB + "/" + path for path in GITHUB_ANDROID_FILES
]


def get_main_branch_from_github_url(url: str) -> str:
    """
    Determine the main branch for the specified URL.
    @param url: Repository URL
    @return: default branch name
    """
    html = None
    try:
        url = normalize_github_url(url)
        html = requests.get(url).text
        if "<title>Rate limit &middot; GitHub</title>" in html:
            raise GithubHTTPRateLimited
        encoded = html.split("default-branch=\"")[1].split('"')[0]
        return base64.b64decode(encoded).decode("utf-8")
    except Exception as e:
        LOG.error(f"html={html}")
        LOG.error(e)
        raise GithubInvalidUrl


def get_repo_releases_from_github_url(url: str) -> list:
    """
    Get releases data for the repository at the specified URL
    https://docs.github.com/en/rest/reference/repos#list-repository-tags
    @param url: Repository URL
    @return: repo tag data
    """
    author, repo = author_repo_from_github_url(url)
    normalized_giturl = normalize_github_url(url)
    url = GithubUrls.TAGS.format(author=author, repo=repo)
    html = requests.get(url).text
    if "<title>Rate limit &middot; GitHub</title>" in html:
        raise GithubHTTPRateLimited
    soup = bs4.BeautifulSoup(html, 'html.parser')
    urls = ["https://github.com" + a['href'] for a in soup.find_all('a')
            if a['href'].startswith("/" + author)]
    releases = []
    current_release = {}
    # NOTE these are ordered!
    for u in urls:
        if u.startswith(normalized_giturl + "/releases/tag/"):
            current_release["name"] = u.split("/tag/")[-1]
        elif u.startswith(normalized_giturl + "/commit/"):
            current_release["commit"] = {
                "sha": u.split("/commit/")[-1],
                "url": u
            }
        elif u.startswith(normalized_giturl + "/archive"):
            if u.endswith(".zip"):
                current_release["zipball_url"] = u
            elif u.endswith(".tar.gz"):
                current_release["tarball_url"] = u
                # this is always the last field
                releases.append(current_release)
                current_release = {}
    return releases


def get_json_url_from_github_url(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get skill.json file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill.json
    """
    branch = branch or get_branch_from_github_url(url)
    # try default github url
    for template in GITHUB_JSON_LOCATIONS:
        try:
            return match_url_template(url, template, branch)
        except GithubInvalidUrl:
            pass
    # try direct url
    try:
        raw_url = blob2raw(url)
        if requests.get(raw_url).status_code == 200:
            return raw_url
    except GithubInvalidUrl:
        pass
    if requests.get(url).status_code == 200:
        return url
    raise GithubFileNotFound


def get_readme_url_from_github_url(url: str,
                                   branch: Optional[str] = None) -> str:
    """
    Get the readme file url for the specified repository
    https://docs.github.com/en/rest/reference/repos#get-a-repository-readme
    @param url: Repository URL
    @param branch: Optional branch to query, otherwise default branch will be used
    @return: url of repository README file
    """
    branch = branch or get_branch_from_github_url(url)
    # try url from default github location
    for template in GITHUB_README_LOCATIONS:
        try:
            return match_url_template(url, template, branch)
        except GithubInvalidUrl:
            pass
    # try direct url
    try:
        return blob2raw(url)
    except GithubInvalidUrl:
        if requests.get(url).status_code == 200:
            return url
    raise GithubReadmeNotFound


def get_desktop_url_from_github_url(url: str,
                                    branch: Optional[str] = None) -> str:
    """
    Get skill.desktop file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill.desktop
    """
    branch = branch or get_branch_from_github_url(url)
    # try default github location
    try:
        return match_url_template(url, GithubUrls.DESKTOP_FILE, branch)
    except GithubInvalidUrl:
        pass

    # try direct url
    try:
        return blob2raw(url)
    except GithubInvalidUrl:
        if requests.get(url).status_code == 200:
            return url
    raise GithubFileNotFound


def get_icon_url_from_github_url(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get skill icon file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill icon
    """
    branch = branch or get_branch_from_github_url(url)
    try:
        desktop = get_desktop_json_from_github_url(url, branch)
    except GithubFileNotFound:
        desktop = {}

    for template in GITHUB_ICON_LOCATIONS:
        try:
            return match_url_template(url, template, branch)
        except GithubInvalidUrl:
            pass

    icon_file = desktop.get("Icon")
    if icon_file:
        # this will assume the icon is in host system, it's not an url
        # lets check if it's present in default github location
        author, repo = author_repo_from_github_url(url)
        url = GithubUrls.ICON.format(author=author, repo=repo,
                                     branch=branch, icon=icon_file)
        if requests.get(url).status_code == 200:
            return blob2raw(url)
        return icon_file
    raise GithubFileNotFound


def get_license_url_from_github_url(url: str,
                                    branch: str = None) -> str:
    """
    Try to get a license file url for the repository at the given url and branch
    @param url: Repository URL
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: url to be used for downloading the repository license file
    """
    branch = branch or get_branch_from_github_url(url)
    # default github locations
    for template in GITHUB_LICENSE_LOCATIONS:
        try:
            return match_url_template(url, template, branch)
        except GithubInvalidUrl:
            pass
    raise GithubLicenseNotFound


def requirements_url_from_github_url(url: str,
                                     branch: Optional[str] = None) -> str:
    """
    Get requirements.txt file URL for the specified repository
    @param url: Repository URL, optionally containing a branch spec
    @param branch: Optional branch spec, otherwise branch from `url` will be used
    @return: Validated URL for repository requirements.txt
    """
    branch = branch or get_branch_from_github_url(url)
    # try default github url
    try:
        return match_url_template(url, GithubUrls.REQUIREMENTS, branch)
    except GithubInvalidUrl:
        raise GithubFileNotFound


def skill_requirements_url_from_github_url(url: str,
                                           branch: Optional[str] = None) -> str:
    """
    Get skill_requirements.txt file URL for the specified repository
    @param url: Repository URL, optionally containing a branch spec
    @param branch: Optional branch spec, otherwise branch from `url` will be used
    @return: Validated URL for repository skill_requirements.txt
    """
    branch = branch or get_branch_from_github_url(url)
    # try default github url
    try:
        return match_url_template(url, GithubUrls.SKILL_REQUIREMENTS, branch)
    except GithubInvalidUrl:
        raise GithubFileNotFound


def manifest_url_from_github_url(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get manifest.yml file URL for the specified repository
    @param url: Repository URL, optionally containing a branch spec
    @param branch: Optional branch spec, otherwise branch from `url` will be used
    @return: Validated URL for repository manifest.yml
    """
    branch = branch or get_branch_from_github_url(url)
    # try default github url
    try:
        return match_url_template(url, GithubUrls.MANIFEST, branch)
    except GithubInvalidUrl:
        raise GithubFileNotFound


# data getters
def get_requirements_from_github_url(url: str,
                                     branch: Optional[str] = None) -> list:
    """
    Get Python requirements from text files in the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: List parsed python requirements
    """
    branch = branch or get_branch_from_github_url(url)
    url = requirements_url_from_github_url(url, branch)
    resp = requests.get(url)
    html = resp.text
    if "<title>Rate limit &middot; GitHub</title>" in html:
        raise GithubHTTPRateLimited
    if not resp.ok:
        raise GithubFileNotFound(f"{resp.url} returned {resp.status_code}:"
                                 f" {resp.content}")
    return [t for t in html.split("\n")
            if t.strip() and not t.strip().startswith("#")]


def get_skill_requirements_from_github_url(url: str,
                                           branch: Optional[str] = None) -> list:
    """
    Get Skill requirements from text files in the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: List parsed skill requirements
    """
    branch = branch or get_branch_from_github_url(url)
    url = skill_requirements_url_from_github_url(url, branch)
    html = requests.get(url).text
    if "<title>Rate limit &middot; GitHub</title>" in html:
        raise GithubHTTPRateLimited
    return [t for t in html.split("\n")
            if t.strip() and not t.strip().startswith("#")]


def get_manifest_from_github_url(url: str,
                                 branch: Optional[str] = None) -> dict:
    """
    Get requirements specified in the repository manifest file
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: dict parsed requirements
    """
    branch = branch or get_branch_from_github_url(url)
    url = manifest_url_from_github_url(url, branch)
    manifest = requests.get(url).text
    if "<title>Rate limit &middot; GitHub</title>" in manifest:
        raise GithubHTTPRateLimited
    data = yaml.safe_load(manifest)
    if not data:
        # most likely just the template full of comments
        raise InvalidManifest
    if 'dependencies' in data:
        return data
    # some skills in the wild have the manifest without the top-level key
    LOG.warning(
        "{url} contains an invalid manifest, attempting recovery".format(
            url=url))
    recovered = {"dependencies": {}}
    if "python" in data:
        recovered["dependencies"]["python"] = data["python"]
    if "skill" in data:
        recovered["dependencies"]["skill"] = data["skill"]
    if "system" in data:
        recovered["dependencies"]["system"] = data["system"]
    if not len(recovered["dependencies"]):
        # suspicious, doesn't follow standard
        raise InvalidManifest
    return recovered


def get_skill_json_from_github_url(url: str,
                                   branch: Optional[str] = None) -> dict:
    """
    Get skill.json file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: data parsed from skill.json
    """
    try:
        branch = branch or get_branch_from_github_url(url)
    except GithubInvalidBranch:
        branch = get_main_branch_from_github_url(url)
    try:
        url = get_json_url_from_github_url(url, branch)
        url = blob2raw(url)
    except GithubInvalidUrl:
        raise GithubFileNotFound
    try:
        res = requests.get(url).text
        if "<title>Rate limit &middot; GitHub</title>" in res:
            raise GithubHTTPRateLimited
        return json.loads(res)
    except:
        # this might happen if branch is considered valid
        # eg, for skill-ddg v0.1.0
        # v0.1 url resolves, but raw url does not
        raise GithubFileNotFound


def get_readme_from_github_url(url: str,
                               branch: Optional[str] = None) -> str:
    """
    Get the readme file contents for the specified repository
    @param url: Repository URL
    @param branch: Optional branch to query, otherwise default branch will be used
    @return: contents of repository README file
    """
    branch = branch or get_branch_from_github_url(url)
    url = get_readme_url_from_github_url(url, branch)
    return requests.get(url).text


def get_license_from_github_url(url: str, branch: str = None) -> str:
    """
    Get string contents of the license file for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: License file contents
    """
    url = get_license_url_from_github_url(url, branch)
    return requests.get(url).text


def get_license_type_from_github_url(url: str,
                                     branch: Optional[str] = None) -> str:
    """
    Determine the License Name for the license of a given repository
    https://docs.github.com/en/rest/reference/licenses#get-the-license-for-a-repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: License Name
    """
    branch = branch or get_branch_from_github_url(url)
    license = get_license_from_github_url(url, branch).lower()
    return parse_license_type(license)


def get_license_data_from_github_url(url: str,
                                     branch: Optional[str] = None) -> dict:
    """
    Get license data for the repository at the given URL and branch
    https://docs.github.com/en/rest/reference/licenses#get-the-license-for-a-repository
    @param url: Repository URL
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: dict license data
    """
    branch = branch or get_branch_from_github_url(url)
    lic = get_license_from_github_url(url, branch)
    return {
        "license_type": parse_license_type(lic),
        "license_text": lic
    }


def get_desktop_from_github_url(url: str,
                                branch: Optional[str] = None) -> str:
    """
    Get skill.desktop file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: skill.desktop string contents
    """
    branch = branch or get_branch_from_github_url(url)
    url = get_desktop_url_from_github_url(url, branch)
    return requests.get(url).text


# data parsers
def get_desktop_json_from_github_url(url: str,
                                     branch: Optional[str] = None) -> dict:
    """
    Get parsed skill.desktop file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: skill.desktop contents parsed into a dict
    """
    branch = branch or get_branch_from_github_url(url)
    desktop = get_desktop_from_github_url(url, branch)
    return desktop_to_json(desktop)


def get_readme_json_from_github_url(url: str, branch: Optional[str] = None) -> dict:
    """
    Get parsed readme file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: Readme contents parsed into a dict
    """
    branch = branch or get_branch_from_github_url(url)
    readme = get_readme_from_github_url(url, branch)
    return readme_to_json(readme)


def get_requirements_json_from_github_url(url: str,
                                          branch: Optional[str] = None) -> dict:
    """
    Get parsed requirements for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: requirements with keys: {python, system, skill}
    """
    branch = branch or get_branch_from_github_url(url)
    data = {"python": [], "system": {}, "skill": []}
    try:
        manif = get_manifest_from_github_url(url, branch)
        data = manif['dependencies'] or {"python": [], "system": {},
                                         "skill": []}
    except GithubFileNotFound:
        pass
    try:
        req = get_requirements_from_github_url(url, branch)
        data["python"] = list(set(data["python"] + req))
    except GithubFileNotFound:
        pass
    try:
        skill_req = get_skill_requirements_from_github_url(url, branch)
        data["skill"] = list(set(data["skill"] + skill_req))
    except GithubFileNotFound:
        pass
    return data


def get_skill_from_github_url(url: str,
                              branch: Optional[str] = None) -> str:
    """
    Get skill icon file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill icon
    """
    # cache_repo_requests(url)  # speed up requests TODO avoid rate limit
    author, repo = author_repo_from_github_url(url)
    data = {
        "authorname": author,
        "foldername": repo,
        "branch": branch,
        "license": "unknown",
        "tags": []
    }
    if not branch:
        try:
            # check if branch is in the url itself
            data["branch"] = branch = get_branch_from_github_url(url)
        except GithubInvalidBranch:
            # let's assume latest release
            try:
                release = get_repo_releases_from_github_url(url)[0]
                data["branch"] = data["version"] = branch = release["name"]
                #data["download_url"] = release["tarball_url"]
            except GithubInvalidBranch:
                pass  # unknown branch...

    url = normalize_github_url(url)
    data["url"] = url
    data["skillname"] = skill_name_from_github_url(url)
    data["requirements"] = get_requirements_json_from_github_url(url, branch)

    # extract branch from .json, should branch take precedence?
    # i think so because user explicitly requested it
    branch = get_branch_from_skill_json_github_url(url, branch)

    # augment with readme data
    try:
        readme_data = get_readme_json_from_github_url(url, branch)
        data = merge_dict(data, readme_data,
                          merge_lists=True, skip_empty=True, no_dupes=True)
    except GithubReadmeNotFound:
        pass

    if branch:  # final, all sources checked by priority order
        data["branch"] = branch
        #data["download_url"] = GithubUrls.DOWNLOAD.format(author=author,
        #                                                  repo=repo,
        #                                                  branch=branch)

    try:
        data["license"] = get_license_type_from_github_url(url, branch)
    except GithubLicenseNotFound:
        pass
    try:
        data["icon"] = get_icon_url_from_github_url(url, branch)
    except GithubFileNotFound:
        pass
    # parse bigscreen flags
    if data["requirements"].get("system"):
        data['systemDeps'] = True
    else:
        data['systemDeps'] = False

    # find logo
    try:
        data["logo"] = get_logo_url_from_github_url(url, branch)
    except GithubFileNotFound as e:
        pass

    # augment with android data
    data["android"] = get_android_json_from_github_url(url, branch)

    # augment with desktop data
    try:
        data["desktop"] = get_desktop_json_from_github_url(url, branch)
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
        data = merge_dict(data, get_skill_json_from_github_url(url, branch),
                          merge_lists=True, skip_empty=True, no_dupes=True)
    except GithubFileNotFound:
        pass

    return data


def get_logo_url_from_github_url(url: str,
                                 branch: Optional[str] = None) -> str:
    """
    Get skill logo file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of skill logo
    """
    branch = branch or get_branch_from_github_url(url)
    for template in GITHUB_LOGO_LOCATIONS:
        try:
            return match_url_template(url, template, branch)
        except GithubInvalidUrl:
            pass
    raise GithubFileNotFound


def get_android_url_from_github_url(url: str,
                                    branch: Optional[str] = None) -> str:
    """
    Get android.json file URL for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: URL of android.json
    """
    branch = branch or get_branch_from_github_url(url)
    for template in GITHUB_ANDROID_JSON_LOCATIONS:
        try:
            return match_url_template(url, template, branch)
        except GithubInvalidUrl:
            pass

    raise GithubFileNotFound


def get_android_json_from_github_url(url: str,
                                     branch: Optional[str] = None) -> dict:
    """
    Get parsed android.json file contents for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: parsed android.json contents
    """
    branch = branch or get_branch_from_github_url(url)
    try:
        url = get_android_url_from_github_url(url, branch)
        return requests.get(url).json()
    except GithubFileNotFound:
        # best guess or throw exception?
        author, repo = author_repo_from_github_url(url)
        try:
            icon = get_icon_url_from_github_url(url, branch)
        except GithubFileNotFound:
            icon = None
        return {'android_icon': icon,
                'android_name': skill_name_from_github_url(url),
                'android_handler': '{repo}.{author}.home'.format(repo=repo,
                                                                 author=author.lower())
                }


def get_branch_from_skill_json_github_url(url: str,
                                          branch: Optional[str] = None):
    """
    Get branch specified in skill.json file for the specified repository
    @param url: Repository URL to query
    @param branch: Optional branch spec, otherwise default branch will be used
    @return: branch spec from skill.json or `branch`
    """
    try:
        branch = branch or get_branch_from_github_url(url)
        if '@' in url:
            url = url.split('@', 1)[0]
    except GithubInvalidBranch:
        branch = "master"  # attempt master branch
    try:
        json_data = get_skill_json_from_github_url(url, branch)
        branch = json_data.get("branch")
        if not branch:
            raise GithubInvalidBranch
    except:
        raise GithubFileNotFound
    return branch


def get_branch_from_latest_release_github_url(url: str) -> str:
    """
    Determine the branch associated with the latest GitHub Release if specified
    @param url: Repository URL
    @return: branch spec of latest tag
    """
    final_url = get_latest_release_github_url(url)
    return get_branch_from_github_url(final_url)


def get_latest_release_github_url(url: str) -> str:
    """
    Determine the main branch for the specified URL.
    https://docs.github.com/en/rest/reference/repos#list-repository-tags
    @param url: Repository URL
    @return: data associated with latest tagged release
    """
    # TODO: API returns dict but raw returns str?
    url = normalize_github_url(url)
    url += "/releases/latest"
    final_url = requests.get(url).url
    if final_url.endswith("/releases"):
        raise GithubInvalidBranch(f"no releases for {url}")
    return final_url

