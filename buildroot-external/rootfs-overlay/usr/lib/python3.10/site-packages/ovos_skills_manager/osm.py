
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message
from ovos_utils.json_helper import merge_dict

from ovos_skills_manager import SkillEntry
from ovos_skills_manager.appstores import AbstractAppstore
from ovos_skills_manager.appstores.andlo import AndloSkillList
from ovos_skills_manager.appstores.mycroft_marketplace import \
    MycroftMarketplace
from ovos_skills_manager.appstores.pling import Pling
from ovos_skills_manager.appstores.ovos import OVOSstore
from ovos_skills_manager.appstores.neon import NeonSkills
from ovos_skills_manager.config import get_config_object
from ovos_skills_manager.exceptions import UnknownAppstore
from ovos_skills_manager.appstores.local import InstalledSkills
from ovos_skills_manager.github import author_repo_from_github_url


class OVOSSkillsManager:
    def __init__(self, bus=None):
        self.config = get_config_object()
        self._boostrap_tracker = {}
        self._threads = []
        self.bus = None

    def bind(self, bus):
        # mycroft messagebus events
        self.bus = bus

    def emit(self, event_name, event_data=None):
        event_data = event_data or {}
        if self.bus:
            self.bus.emit(Message(event_name, event_data))

    def get_active_appstores(self, bootstrap:bool=False):
        stores = {}
        for appstore_id in self.config["appstores"]:
            if self.config["appstores"][appstore_id]["active"]:
                if bootstrap and appstore_id not in self._boostrap_tracker:
                    self._boostrap_tracker[appstore_id] = True
                elif bootstrap and appstore_id in self._boostrap_tracker:
                    bootstrap = False
                stores[appstore_id] = self.get_appstore(appstore_id,
                                                        bootstrap=bootstrap)
        return stores

    def get_appstore(self, appstore_id: str, bootstrap:bool=True):
        if self.config["appstores"][appstore_id]["active"]:
            parse_github = self.config["appstores"][appstore_id]["parse_github"]
            store = self.name_to_appstore(appstore_id)
            if bootstrap and appstore_id not in self._boostrap_tracker:
                self._boostrap_tracker[appstore_id] = True
            elif bootstrap and appstore_id in self._boostrap_tracker:
                bootstrap = False
            return store(parse_github=parse_github, bootstrap=bootstrap)
        return None

    @staticmethod
    def name_to_appstore(name: str) -> AbstractAppstore:
        if name in ["pling", "bigscreen"]:
            return Pling
        elif name in ["mycroft", "mycroft_marketplace"]:
            return MycroftMarketplace
        elif name in ["andlo", "andlo_skill_list"]:
            return AndloSkillList
        elif name in ["ovos", "ovos_appstore", "ovos_marketplace"]:
            return OVOSstore
        elif name in ["neon", "neon_gecko", "neon_skills"]:
            return NeonSkills
        elif name in ["local", "local_skills", "installed",
                      "installed_skills"]:
            return InstalledSkills
        else:
            raise UnknownAppstore

    def clear_cache(self, appstore_id:str=None):
        if appstore_id:
            self.get_appstore(appstore_id).clear_cache()
        else:
            for appstore in self.appstores:
                appstore.clear_cache()

    def validate_appstore_name(self, appstore: str):
        if appstore in ["pling", "bigscreen"]:
            appstore = "pling"
        elif appstore in ["mycroft", "mycroft_marketplace"]:
            appstore = "mycroft_marketplace"
        elif appstore in ["andlo", "andlo_skill_list"]:
            appstore = "andlo_skill_list"
        elif appstore in ["ovos", "ovos_appstore", "ovos_marketplace"]:
            appstore = "ovos"
        elif appstore in ["neon", "neon_gecko", "neon_skills"]:
            appstore = "neon"
        elif appstore in ["local", "local_skills", "installed",
                          "installed_skills"]:
            appstore = "local"
        elif appstore not in self.config["appstores"]:
            raise UnknownAppstore(f"Unknown Appstore: {appstore}")
        return appstore

    def enable_appstore(self, appstore_id: str):
        appstore_id = self.validate_appstore_name(appstore_id)
        self.config["appstores"][appstore_id]["active"] = True
        self.emit("osm.store.enabled", {"store": appstore_id})

    def set_appstore_priority(self, appstore_id: str, priority: int):
        appstore_id = self.validate_appstore_name(appstore_id)
        self.config["appstores"][appstore_id]["priority"] = priority
        self.emit("osm.store.priority.change", {"store": appstore_id,
                                                "priority": priority})

    def set_appstore_auth_token(self, appstore_id: str, token: str):
        appstore_id = self.validate_appstore_name(appstore_id)
        self.config["appstores"][appstore_id]["auth_token"] = token
        self.emit("osm.store.token.change", {"store": appstore_id})

    def disable_appstore(self, appstore_id: str):
        appstore_id = self.validate_appstore_name(appstore_id)
        self.config["appstores"][appstore_id]["active"] = False
        self.emit("osm.store.disabled", {"store": appstore_id})

    def sync_appstores(self, merge:bool=False, new_only:bool=False, threaded:bool=False):
        stores = self.get_active_appstores()
        self.emit("osm.sync.start")
        for appstore_id in stores:
            LOG.info("Syncing skills from " + appstore_id)
            self.emit("osm.store.sync.start", {"store": appstore_id})
            try:
                store = stores[appstore_id]
                store.authenticate()
                store.sync_skills_list(merge, new_only)
                store.clear_authentication()
            except Exception as e:
                self.emit("osm.store.sync.error",
                          {"store": appstore_id, "error": str(e)})
            self.emit("osm.store.sync.finish", {"store": appstore_id})
        self.emit("osm.sync.finish")

    @property
    def total_skills(self):
        return sum([s.total_skills() for s in self.appstores])

    @property
    def appstores(self):
        stores = []
        for appstore_id in self.config["appstores"]:
            store = self.get_appstore(appstore_id)
            if not store:
                continue
            priority = self.config["appstores"][appstore_id]["priority"]
            stores.append((store, priority))
        return [s[0] for s in sorted(stores, key=lambda k: k[1])]

    def search_skills(self, name: str, as_json:bool=False, fuzzy:bool=True, thresh:float=0.85,
                      ignore_case:bool=True):
        self.emit("osm.search.start",
                  {"query": name, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "generic"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills(name, as_json, fuzzy,  thresh,
                                             ignore_case):
                self.emit("osm.search.store.result",
                          {"query": name, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "generic", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": name, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "generic"})

    def search_skills_by_id(self, skill_id: str, as_json:bool=False, fuzzy:bool=False,
                            thresh:float=0.85, ignore_case:bool=True):
        """ skill_id is repo.author , case insensitive,
        searchs by name and filters results by author """
        self.emit("osm.search.start",
                  {"query": skill_id, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "id"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_id(skill_id, as_json,
                                                   fuzzy=fuzzy,
                                                   ignore_case=ignore_case,
                                                   thresh=thresh):
                self.emit("osm.search.store.result",
                          {"query": skill_id, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "id", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": skill_id, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "id"})

    def search_skills_by_name(self, name:str, as_json:bool=False,
                              fuzzy:bool=True, thresh:float=0.85, ignore_case:bool=True):
        self.emit("osm.search.start",
                  {"query": name, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "name"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_name(name, as_json, fuzzy,
                                                     thresh, ignore_case):
                self.emit("osm.search.store.result",
                          {"query": name, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "name", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": name, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "name"})

    def search_skills_by_url(self, url:str, as_json:bool=False):
        self.emit("osm.search.start",
                  {"query": url, "search_type": "url"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_url(url, as_json):
                store.clear_authentication()
                self.emit("osm.search.finish",
                          {"query": url, "search_type": "url",
                           "skill": skill.json})
                yield skill
        self.emit("osm.search.finish",
                  {"query": url, "search_type": "url"})

    def search_skills_by_category(self, category:str, as_json:bool=False,
                                  fuzzy:bool=True, thresh:float=0.85, ignore_case:bool=True):
        self.emit("osm.search.start",
                  {"query": category, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "category"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_category(category, as_json,
                                                         fuzzy, thresh,
                                                         ignore_case):
                self.emit("osm.search.store.result",
                          {"query": category, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "category", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": category, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "category"})

    def search_skills_by_author(self, authorname:str, as_json:bool=False,
                                fuzzy:bool=True, thresh:float=0.85, ignore_case:bool=True):
        self.emit("osm.search.start",
                  {"query": authorname, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "author"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_author(authorname, as_json,
                                                       fuzzy, thresh,
                                                       ignore_case):
                self.emit("osm.search.store.result",
                          {"query": authorname, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "author", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": authorname, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "author"})

    def search_skills_by_tag(self, tag:str, as_json:bool=False,
                             fuzzy:bool=True, thresh:float=0.85, ignore_case:bool=True):
        self.emit("osm.search.start",
                  {"query": tag, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "tag"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_tag(tag, as_json, fuzzy,
                                                    thresh, ignore_case):
                self.emit("osm.search.store.result",
                          {"query": tag, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "tag", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": tag, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "tag"})

    def search_skills_by_description(self, value: str, as_json:bool=False,
                                     fuzzy:bool=True, thresh:float=0.85,
                                     ignore_case:bool=True):
        self.emit("osm.search.start",
                  {"query": value, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "description"})
        for store in self.appstores:
            store.authenticate()
            for skill in store.search_skills_by_description(value, as_json,
                                                            fuzzy, thresh,
                                                            ignore_case):
                self.emit("osm.search.store.result",
                          {"query": value, "thresh": thresh, "fuzzy": fuzzy,
                           "ignore_case": ignore_case,
                           "search_type": "description", "skill": skill.json,
                           "store": store.appstore_id})
                yield skill
            store.clear_authentication()
        self.emit("osm.search.finish",
                  {"query": value, "thresh": thresh, "fuzzy": fuzzy,
                   "ignore_case": ignore_case, "search_type": "description"})

    @staticmethod
    def skill_entry_from_url(url: str):
        """
        Builds a minimal SkillEntry object from the passed GitHub URL to use for skill installation
        :param url: URL of skill to install
        :return: SkillEntry object with url, branch, requirements, and authorname populated
        """
        from ovos_skills_manager.exceptions import GithubInvalidBranch, GithubFileNotFound
        from ovos_skills_manager.github import get_branch_from_github_url, normalize_github_url, get_requirements_json,\
            get_skill_json
        from ovos_skills_manager.skill_entry import SkillEntry
        try:
            branch = get_branch_from_github_url(url)
        except GithubInvalidBranch:
            branch = None
        url = normalize_github_url(url)
        requirements = get_requirements_json(url, branch)
        requirements["system"] = {k: v.split() for k, v in requirements.get("system", {}).items()}
        try:
            json = get_skill_json(url, branch)
            requirements = merge_dict(requirements, json.get("requirements", {}),
                                      merge_lists=True, skip_empty=True, no_dupes=True)
        except GithubFileNotFound:
            json = {"authorname": author_repo_from_github_url(url)[0]}
        return SkillEntry.from_json({"url": url,
                                     "branch": branch,
                                     "requirements": requirements,
                                     "authorname": json.get("authorname")}, False)

    def install_skill_from_url(self, url: str, skill_dir:str=None):
        """
        Installs a Skill from the passed url
        :param url: Git url of skill to install (including optional branch spec)
        :param skill_dir: Skills directory to install to (skill unpacked to {folder}/{skill.uuid})
        """
        self.install_skill(self.skill_entry_from_url(url), skill_dir)

    def install_skill(self, skill: SkillEntry, folder=None):
        """
        Installs a SkillEntry with any required auth_token
        :param skill: Skill to install
        :param folder: Skills directory to install to (skill unpacked to {folder}/{skill.uuid})
        """
        self.emit("osm.install.start",
                  {"folder": folder, "skill": skill.json})
        store = None
        try:
            self.validate_appstore_name(skill.appstore)
            store = self.get_appstore(skill.appstore)
            store.authenticate(bootstrap=False)
        except UnknownAppstore as e:
            LOG.info(f"Skill Entry from unknown appstore: {e}")
        except Exception as e:
            LOG.exception(e)
            self.emit("osm.install.error",
                      {"folder": folder, "skill": skill.json, "error": str(e)})
        try:
            skill.install(folder)
        except Exception as e:
            LOG.error(e)
            self.emit("osm.install.error",
                      {"folder": folder, "skill": skill.json, "error": str(e)})
        if store:
            store.clear_authentication()
        self.emit("osm.install.finish",
                  {"folder": folder, "skill": skill.json})

    def __iter__(self):
        for store in self.appstores:
            for skill in store:
                yield skill
