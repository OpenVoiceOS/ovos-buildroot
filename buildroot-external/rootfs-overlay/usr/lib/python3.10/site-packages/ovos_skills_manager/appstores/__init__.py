import os
import re
import shutil
from typing import Optional

from json_database import JsonDatabaseXDG, JsonConfigXDG
from json_database.search import Query
from ovos_utils import create_daemon
from ovos_utils.log import LOG
from os.path import join, dirname, isfile
from ovos_skills_manager import SkillEntry
from ovos_skills_manager.exceptions import AuthenticationError, GithubInvalidUrl
from ovos_skills_manager.session import set_github_token, clear_github_token
from ovos_skills_manager.github import get_branch_from_github_url,\
    normalize_github_url, GithubInvalidBranch


class AbstractAppstore:
    def __init__(self, name:str, parse_github:bool=False, appstore_id:Optional[str]=None,
                 bootstrap:bool=False):
        self.name = name
        default_id = re.sub(r'[^\w]', ' ',
                            name.lower().replace("_", " ").replace("-", " "))
        self.appstore_id = appstore_id or default_id
        self.db = JsonDatabaseXDG(name)
        self.parse_github = parse_github
        if bootstrap:
            try:
                self.bootstrap()
            except AuthenticationError:
                pass

    def authenticate(self, auth_token:Optional[str]=None, bootstrap:bool=True):
        if auth_token is None:
            auth_token = JsonConfigXDG("OVOS-SkillsManager", subfolder="OpenVoiceOS")["appstores"]\
                .get(self.appstore_id, {}).get("auth_token")
        if auth_token:
            set_github_token(auth_token)
            if bootstrap:
                self.bootstrap()

    @staticmethod
    def clear_authentication():
        clear_github_token()

    def bootstrap(self, new_only:bool=True):
        base_db = join(dirname(dirname(__file__)), "res",
                       self.db.name + ".jsondb")
        if not len(self.db):
            os.makedirs(dirname(self.db.path), exist_ok=True)
            LOG.info("Bootstrapping {database}, this might take a "
                     "while!".format(database=self.name))
            if isfile(base_db):
                LOG.debug("Bootstrapping from bundled skill list")
                shutil.copyfile(base_db, self.db.path)
                self.db.reset()
            else:
                LOG.debug("Downloading skill list")
                self.sync_skills_list(new_only=new_only)

    def clear_cache(self):
        if isfile(self.db.path):
            LOG.debug("Removing appstore cache " + self.db.path)
            os.remove(self.db.path)
            self.db.reset()

    def get_skills_list(self, skiplist:list=None):
        return []

    def sync_skills_list(self, merge:bool=False, new_only:bool=False):
        skiplist = None
        if new_only:
            skiplist = [s["url"] for s in self.db if s.get("url")]

        skills = self.get_skills_list(skiplist=skiplist) or []
        for skill in skills:
            LOG.info("Synced skill: " + skill.url)

            for old_skill in self.search_skills_by_url(skill.url,
                                                       as_json=True):
                item_id = self.db.get_item_id(old_skill)
                if merge:
                    LOG.debug("Merging skill data")
                    self.db.merge_item(skill.json, item_id)
                else:
                    LOG.debug("Removing old skill from db")
                    self.db.remove_item(item_id)
            if not merge:
                LOG.debug("Adding new skill to db")
                self.db.add_item(skill.json)
            self.db.commit()

    def sync_skills_list_threaded(self, merge:bool=False, new_only:bool=False):
        return create_daemon(self.sync_skills_list, (merge, new_only))

    def total_skills(self):
        return len(self.db)

    def search_skills_by_name(self, name:str, as_json:bool=False,
                              fuzzy:bool=True, thresh:float=0.85, ignore_case=True):
        query = Query(self.db)
        query.contains_value('skillname', name, fuzzy, thresh, ignore_case)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id

        if as_json:
            return query.result
        return [SkillEntry.from_json(s, False) for s in results]

    def search_skills_by_id(self, skill_id:str, as_json=False, fuzzy=False,
                            thresh:float=0.85, ignore_case=True):
        """ skill_id is repo.author , case insensitive,
        searchs by name and filters results by author """
        name = ".".join(skill_id.split(".")[:-1])
        author = skill_id.rsplit('.', 1)[1]

        query = Query(self.db)
        query.contains_value('skillname', name, fuzzy, thresh, ignore_case)
        query.value_contains_token('authorname', author, fuzzy, thresh,
                                   ignore_case)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id

        if as_json:
            return query.result
        return [SkillEntry.from_json(s, False) for s in results]

    def search_skills_by_url(self, url:str, as_json=False):
        query = Query(self.db)
        try:
            # if branch implicit in url, be sure to use it!
            branch = get_branch_from_github_url(url)
        except GithubInvalidBranch:
            branch = None
        try:
            url = normalize_github_url(url)
        except GithubInvalidUrl:
            return []
        query.equal("url", url, ignore_case=True)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id
            if branch:
                # TODO what if branch does not exist? should throw exception
                results[idx]["branch"] = branch
        if as_json:
            return query.result
        return [SkillEntry.from_json(s, parse_github=False) for s in results]

    def search_skills_by_category(self, category:str, as_json=False,
                                  fuzzy=True, thresh:float=0.85, ignore_case=True):
        query = Query(self.db)
        query.contains_value('category', category, fuzzy, thresh)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id
        if as_json:
            return query.result
        return [SkillEntry.from_json(s, False) for s in results]

    def search_skills_by_author(self, authorname:str, as_json=False,
                                fuzzy=True, thresh:float=0.85, ignore_case=True):
        query = Query(self.db)
        query.value_contains_token('authorname', authorname,
                                   fuzzy, thresh, ignore_case)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id
        if as_json:
            return query.result
        return [SkillEntry.from_json(s, False) for s in results]

    def search_skills_by_tag(self, tag:str, as_json:bool=False,
                             fuzzy:bool=True, thresh:float=0.85, ignore_case:bool=True):
        query = Query(self.db)
        query.contains_value('tags', tag, fuzzy, thresh, ignore_case)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id
        if as_json:
            return query.result
        return [SkillEntry.from_json(s, False) for s in results]

    def search_skills_by_description(self, value, as_json:bool=False,
                                     fuzzy:bool=True, thresh=0.85,
                                     ignore_case:bool=True):
        query = Query(self.db)
        query.value_contains_token('description', value,
                                   fuzzy, thresh, ignore_case)
        results = query.result
        for idx in range(0, len(results)):
            if "appstore" not in results[idx]:
                results[idx]["appstore"] = self.appstore_id
        if as_json:
            return query.result
        return [SkillEntry.from_json(s, False) for s in results]

    def search_skills(self, query:str, as_json:bool=False, fuzzy:bool=True,
                      thresh:float=0.85, ignore_case:bool=True):
        # check for exact url matches
        url_skills = self.search_skills_by_url(query, as_json)
        if url_skills:
            return url_skills

        # check for query in name
        name_skills = self.search_skills_by_name(query, as_json, fuzzy,
                                                 thresh, ignore_case)
        if name_skills:
            return name_skills

        # check for author
        author_skills = self.search_skills_by_author(query, as_json, fuzzy,
                                                     thresh, ignore_case)
        if author_skills:
            return author_skills

        # check in tags and description
        tag_skills = self.search_skills_by_tag(query, as_json, fuzzy,
                                               thresh, ignore_case)
        desc_skills = self.search_skills_by_description(query, as_json, fuzzy,
                                                        thresh, ignore_case)
        res = desc_skills + tag_skills  # TODO: This may include duplicates DM
        if res:
            return res

        # last chance... very generic search
        author_skills = self.search_skills_by_author(query, as_json, fuzzy,
                                                     thresh - 0.25,
                                                     ignore_case)
        cat_skills = self.search_skills_by_category(query, as_json, fuzzy,
                                                    thresh, ignore_case)
        return author_skills + cat_skills

    def print(self):
        self.db.print()

    def __iter__(self):
        for s in self.db:
            yield SkillEntry.from_json(s, parse_github=False)
