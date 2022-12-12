import json
import shutil

from os import mkdir
from os.path import isfile, exists, expanduser, join, isdir
from typing import Optional, Union

from ovos_skills_manager.local_skill import get_skill_data_from_directory
from ovos_skills_manager.session import SESSION as requests
from ovos_skills_manager.exceptions import GithubInvalidUrl, \
    JSONDecodeError, GithubFileNotFound, SkillEntryError, GithubInvalidBranch
from ovos_skills_manager.github import download_url_from_github_url, \
    get_branch, get_skill_data, normalize_github_url, get_branch_from_github_url, author_repo_from_github_url
from ovos_utils.json_helper import merge_dict
from ovos_utils.skills import blacklist_skill, whitelist_skill, \
    make_priority_skill, get_skills_folder
from ovos_skill_installer import install_skill
from ovos_skills_manager.requirements import install_system_deps, pip_install
from ovos_utils.log import LOG
from ovos_utils.enclosure import detect_enclosure

from ovos_skills_manager.utils import parse_python_dependencies


class SkillEntry:
    def __init__(self, data=None):
        self._data = data or {}

    @property
    def uuid(self) -> str:
        # a unique identifier
        # github_repo.github_author , case insensitive
        # should be guaranteed to be unique
        if self.url:
            try:
                author, folder = author_repo_from_github_url(self.url)
            except Exception as e:
                LOG.error(e)
                return ""
        else:
            LOG.warning(f"Skill installation from local source; uuid may have collisions")
            author = self.skill_author if self.skill_author else None
            folder = self.skill_folder if self.skill_folder else None
        if folder and author:
            return f"{folder}.{author}".lower()
        else:
            LOG.warning(f"repo or author not defined, skill uuid cannot be determined!")
            return ""

    @property
    def json(self) -> dict:
        return self._data

    # constructors
    @staticmethod
    def from_json(data: Union[str, dict], parse_github: bool = True):
        if isinstance(data, str):
            if data.startswith("http"):
                url = data
                if "github" in url:
                    data = {"url": url}
                    # repo is parsed in github info step below,
                    # branch detected when parsing data dict
                else:
                    try:
                        res = requests.get(url).text
                        data = json.loads(res)
                    except JSONDecodeError:
                        raise GithubFileNotFound
            elif isfile(data):
                with open(data) as f:
                    data = json.load(f)
            else:
                data = json.loads(data)

        if not isinstance(data, dict):
            # TODO new exception
            raise ValueError("unrecognized format")

        # augment with github info
        if parse_github:
            url = data.get("url", "")
            if "github" in url:
                try:
                    github_data = get_skill_data(url, data.get("branch"))
                    data = merge_dict(github_data, data, merge_lists=True,
                                      skip_empty=True, no_dupes=True)
                    parse_python_dependencies(data["requirements"].get("python"), requests.headers.get("Authorization"))
                except GithubInvalidUrl as e:
                    raise e
        return SkillEntry(data)

    @staticmethod
    def from_github_url(url, branch: str = None, parse_github: bool = True):
        if not branch:
            try:
                branch = get_branch_from_github_url(url)
            except GithubInvalidBranch:
                branch = None
        url = normalize_github_url(url)
        return SkillEntry.from_json({"url": url, "branch": branch},
                                    parse_github=parse_github)

    @staticmethod
    def from_directory(skill_dir: str, github_token: Optional[str] = None):
        """
        Build a SkillEntry for a local skill directory
        @param skill_dir: path to skill
        @param github_token: optional Github token for private dependencies
        @return: SkillEntry representation of the specified skill
        """
        skill_dir = expanduser(skill_dir)
        if not isdir(skill_dir):
            raise ValueError(f"{skill_dir} is not a valid directory")

        data = get_skill_data_from_directory(skill_dir)
        parse_python_dependencies(data["requirements"].get("python"),
                                  github_token)
        return SkillEntry.from_json(data, False)

    # properties
    @property
    def url(self) -> str:
        return self.json.get("url") or ""

    @property
    def appstore(self) -> str:
        return self.json.get("appstore") or "unknown"

    @property
    def skill_name(self) -> str:
        return_val = self.json.get("skillname") or self.json.get("name")
        if self.url and not return_val:
            _, return_val = author_repo_from_github_url(self.url)
        return return_val or ""

    @property
    def skill_short_description(self) -> str:
        # TODO consider using OpenJarbas/quebra_frases or another chunker
        return self.json.get("short_description") or \
               self.skill_description.split("\n")[0]

    @property
    def skill_description(self) -> str:
        return self.json.get("description") or ("{1} by {0}".format(
                *author_repo_from_github_url(self.url)) if self.url else "No description")

    @property
    def skill_folder(self) -> str:
        return_val = self.json.get("foldername") or ""
        if self.url and not return_val:
            author, repo = author_repo_from_github_url(self.url)
            return_val = f"{repo}.{author}"
        return return_val

    @property
    def skill_category(self) -> str:
        return self.json.get("category") or "VoiceApp"

    @property
    def skill_icon(self) -> str:
        # TODO bundle a default icon
        return self.json.get("icon") or "https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/robot.svg"

    @property
    def skill_author(self) -> str:
        return self.json.get("authorname") or (self.url.split("/")[-2] if self.url and "/" in self.url else "")

    @property
    def skill_tags(self) -> list:
        return self.json.get("tags") or []

    @property
    def skill_examples(self) -> list:
        return self.json.get("examples") or []

    @property
    def homescreen_msg(self) -> str:
        home_screen_msg = "{skill_folder}.{author}.home".lower()
        return home_screen_msg.format(skill_folder=self.skill_folder,
                                      author=self.skill_author)

    @property
    def branch(self) -> str:
        try:
            return self.json.get("branch") or get_branch(self.url)
        except GithubInvalidUrl:
            return ""

    @property
    def branch_overrides(self) -> dict:
        return self.json.get("branch_overrides") or {}

    @property
    def download_url(self) -> str:
        """ generated from github url directly"""
        try:
            return download_url_from_github_url(self.url, self.branch)
        except GithubInvalidUrl:
            return ""

    @property
    def default_download_url(self) -> str:
        """ sugar / backwards compat """
        return self.download_url

    @property
    def requirements(self) -> dict:
        try:
            return self.json.get("requirements") or \
                   get_skill_data(self.url, self.branch).get("requirements") \
                   or {}
        except GithubFileNotFound:
            return {}

    @property
    def license(self) -> str:
        return self.json.get("license") or "unknown"

    @property
    def desktop_file(self) -> str:
        return self.generate_desktop_file()

    # generators
    def generate_desktop_json(self):
        return {'Terminal': 'false',
                'Type': 'Application',
                'Name': self.skill_name,
                'Exec': 'mycroft-gui-app --hideTextInput --skill=' +
                        self.homescreen_msg,
                'Icon': self.skill_icon,
                'Categories': "VoiceApp",
                'StartupNotify': 'false',
                'X-DBUS-StartupType': 'None',
                'X-KDE-StartupNotify': 'false'}

    def generate_desktop_file(self):
        desktop_json = self.json.get("desktop") or self.generate_desktop_json()
        # icon renamed
        base_name = ".".join([self.skill_folder, self.skill_author]).lower()
        desktop_json["Icon"] = base_name + self.skill_icon.split(".")[-1]

        desktop_file = "[Desktop Entry]"
        for k in desktop_json:
           if desktop_json[k]:
                desktop_file += "\n" + k + "=" + desktop_json[k]
        return desktop_file

    def generate_readme(self):
        template = \
            """# <img src='{icon}' card_color='#000000' width='50' height='50' style='vertical-align:bottom'/> {title}
{one_liner}

## About
{description}

## Examples
{examples}

## Credits
{author}

## Category
{category}

## Tags
{tags}
"""
        return template.format(title=self.skill_name,
                               description=self.skill_description,
                               category="**" + self.skill_category + "**",
                               author=self.skill_author,
                               icon=self.skill_icon,
                               one_liner=self.skill_short_description,
                               examples="\n* " + "\n* ".join(self.skill_examples),
                               tags=" ".join(["#" + t for t in self.skill_tags]))

    # actions
    def blacklist(self):
        blacklist_skill(self.skill_folder)

    def whitelist(self):
        whitelist_skill(self.skill_folder)

    def make_priority(self):
        make_priority_skill(self.skill_folder)

    def download(self, folder:str=None) -> bool:
        folder = folder or get_skills_folder()
        if self.download_url.endswith(".tar.gz"):
            ext = "tar.gz"
        elif "zipball" in self.download_url:
            ext = "zip"
        else:
            ext = self.download_url.split(".")[-1]
        file = self.skill_folder + "." + ext
        url = self.download_url
        skill_dirname = self.uuid
        if not skill_dirname:
            raise SkillEntryError(f"OSM installation of {self.skill_name or 'unknown skill'} failed!"
                                  f" uuid was not defined.")
        return install_skill(url, folder, file, session=requests,
                             skill_folder_name=skill_dirname)

    def install(self,
                folder:Optional[str]=None,
                default_branch:str="master",
                platform:Optional[str]=None,
                update:bool=True) -> bool:
        if not folder:
            folder = get_skills_folder()
        if not update and self.is_previously_installed(folder):
            return False
        if self.branch_overrides:
            try:
                platform = platform or detect_enclosure()
            except Exception as e:
                LOG.error("Failed to detect platform")
                raise e
            if platform in self.branch_overrides:
                branch = self.branch_overrides[platform]
                if branch != self.branch:
                    LOG.info("Detected platform specific branch:" + branch)
                    skill = SkillEntry.from_github_url(self.url, branch)
                    return skill.install(folder, default_branch)

        LOG.info("Installing skill: {url} from branch: {branch}".format(
            url=self.url, branch=self.branch))

        skills = self.requirements.get("skill", [])
        if skills:
            LOG.info('Installing required skills')
        for s in skills:
            skill = SkillEntry.from_github_url(s)
            skill.install(folder, default_branch)

        system = self.requirements.get("system")
        if system:
            LOG.info('Installing system requirements')
            install_system_deps(system)

        pyth = self.requirements.get("python")
        if pyth:
            LOG.info('Running pip install')
            pip_install(pyth)

        LOG.info("Downloading " + self.url)
        updated = self.download(folder)
        # TODO: desktop file generation has been disabled for the time being
        '''
        if self.json.get("desktopFile"):
            LOG.info("Creating desktop entry")
            # TODO support system wide? /usr/local/XXX ?
            desktop_dir = expanduser("~/.local/share/applications")
            icon_dir = expanduser("~/.local/share/icons")
            # ensure directories exist
            if not exists(desktop_dir):
                mkdir(desktop_dir)
            if not exists(icon_dir):
                mkdir(icon_dir)

            # copy the files to a unique path, this way duplicate file names
            # dont overwrite each other, eg, several skills with "icon.png"
            base_name = ".".join([self.skill_folder, self.skill_author]).lower()

            # copy icon file
            icon_file = join(icon_dir,
                             base_name + "." + self.skill_icon.split(".")[-1])
            if self.skill_icon.startswith("http"):
                content = requests.get(self.skill_icon).content
                with open(icon_file, "wb") as f:
                    f.write(content)
            elif isfile(self.skill_icon):
                shutil.copyfile(self.skill_icon, icon_file)

            # copy .desktop file
            desktop_file = join(desktop_dir, base_name + ".desktop")
            with open(desktop_file, "w") as f:
                f.write(self.desktop_file)
            '''
        return updated

    def update(self,
               folder:Optional[str]=None,
               default_branch:str="master",
               platform:Optional[str]=None) -> bool:
        # convenience method
        return self.install(folder, default_branch, platform, update=True)

    def is_previously_installed(self, folder=None):
        folder = folder or get_skills_folder()
        # TODO If self.uuid is None, this skill entry is somehow malformed,
        # probably because it was created manually with partial input.
        # Something should happen in this case, but what?
        return isdir(join(folder, self.uuid)) if self.uuid else False

    def __repr__(self):
        if not self.skill_name:
            return self.url or repr(self.json)
        return self.skill_name + " " + self.url

    def __eq__(self, other):
        return self.json == other.json
