import json
import os
import re
from copy import deepcopy
from os import makedirs
from os.path import dirname, expanduser, join, isfile, isdir

from json_database import JsonStorage
from ovos_config import Configuration
from ovos_utils import camel_case_split
from ovos_utils.configuration import get_xdg_config_save_path, get_xdg_data_save_path, get_xdg_data_dirs

from ovos_backend_client.api import DeviceApi


def get_display_name(skill_name: str):
    """Splits camelcase and removes leading/trailing "skill"."""
    skill_name = skill_name.replace("_", " ").replace("-", " ")
    skill_name = re.sub(r'(^[Ss]kill|[Ss]kill$)', '', skill_name)
    return camel_case_split(skill_name).title().strip()


class RemoteSkillSettings:
    """ WARNING: selene backend does not use proper skill_id, if you have
    skills with same name but different author settings will overwrite each
    other on the backend, THIS CLASS IS NOT 100% SAFE in mycroft-core

    mycroft-core uses msm to generate weird metadata, removes author and munges github branch names into id
    see: https://github.com/MycroftAI/mycroft-skills-manager/blob/master/msm/skill_entry.py#L145

    ovos-core uses the proper deterministic skill_id and can be used safely
    if running in mycroft-core you want to use remote_id=self.settings_meta.skill_gid

    you can define arbitrary strings as skill_id to use this as a datastore

    skill matching is currently done by checking "if {skill_id} in string"
    """

    def __init__(self, skill_id, settings=None, meta=None, url=None, version="v1", remote_id=None):
        self.api = DeviceApi(url, version)
        self.skill_id = skill_id
        self.identifier = remote_id or \
                          self.selene_gid if not skill_id.startswith("@") else skill_id
        self.settings = settings or {}
        self.meta = meta or {}
        self.local_path = join(get_xdg_config_save_path(), 'skills', self.skill_id, 'settings.json')
        if not self.settings:
            self.load()

    @property
    def selene_gid(self):
        if self.api.identity.uuid:
            return f'@{self.api.identity.uuid}|{self.skill_id}'
        return f'@|{self.skill_id}'

    @staticmethod
    def _settings2meta(settings):
        """ generates basic settingsmeta fields"""
        fields = []
        for k, v in settings.items():
            if k.startswith("_"):
                continue
            label = k.replace("-", " ").replace("_", " ").title()
            if isinstance(v, bool):
                fields.append({
                    "name": k,
                    "type": "checkbox",
                    "label": label,
                    "value": str(v).lower()
                })
            if isinstance(v, str):
                fields.append({
                    "name": k,
                    "type": "text",
                    "label": label,
                    "value": v
                })
            if isinstance(v, int) or isinstance(v, float):
                fields.append({
                    "name": k,
                    "type": "number",
                    "label": label,
                    "value": str(v)
                })
        return fields

    def generate_meta(self):
        """ auto generate settings meta info for any valid value defined in settings but missing in meta"""
        names = []
        if "sections" not in self.meta:
            self.meta["sections"] = []
        for s in self.meta["sections"]:
            names += [f["name"] for f in s.get("fields", [])]
        new_meta = self._settings2meta(
            {k: v for k, v in self.settings.items()
             if k not in names and not k.startswith("_")})
        for idx, s in enumerate(self.meta["sections"]):
            if s.get("name") == "Skill Settings":
                self.meta["sections"][idx] = {"name": "Skill Settings", "fields": new_meta}
                break
        else:
            self.meta["sections"].append({"name": "Skill Settings", "fields": new_meta})
        # TODO auto update in backend ?

    def download(self, filter_uuid=False):
        """
        download skill settings for this skill from selene

        WARNING: mycroft-core does not use proper skill_id, if you have
        skills with same name but different author settings will overwrite each
        other on the backend, THIS METHOD IS NOT SAFE in mycroft-core

        mycroft-core uses msm to generate weird metadata, removes author and munges github branch names into id
        if running in mycroft-core you want to use remote_id=self.settings_meta.skill_gid

        ovos-core uses the proper deterministic skill_id and can be used safely
        """
        data = self.api.get_skill_settings_v1()

        def match_settings(x, against):
            # this is a mess, possible keys seen by logging data
            # - @|XXX
            # - @{uuid}|XXX
            # - XXX

            # where XXX has been observed to be
            # - {skill_id}  <- ovos-core
            # - {msm_name} <- mycroft-core
            #   - {mycroft_marketplace_name} <- all default skills
            #   - {MycroftSkill.name} <- sometimes sent to msm (very uncommon)
            #   - {skill_id.split(".")[0]} <- fallback msm name
            # - XXX|{branch} <- append by msm (?)
            # - {whatever we feel like uploading} <- SeleneCloud utils

            for sets in x:
                fields = sets["identifier"].split("|")
                skill_id = fields[0]
                uuid = None
                if len(fields) >= 2 and fields[0].startswith("@"):
                    uuid = fields[0].replace("@", "")
                    skill_id = fields[1]

                # setting belong to another device
                if uuid and uuid != self.api.uuid:
                    # shared_settings flag
                    # do not return settings for same skill from other devices
                    # this should not be relied on, no assurance that uuid is part of gid
                    # selene assumes settings are shared, only cares about skill versions not devices
                    # TODO - proper integration with local backend (?)
                    if filter_uuid:
                        continue

                if skill_id == against or sets["identifier"] == against:
                    return self.deserialize(sets)

        s = match_settings(data, self.identifier) or \
            match_settings(data, self.skill_id)

        if s:
            self.meta = s.meta
            self.settings = s.settings
            # update actual identifier from selene
            self.identifier = s.identifier

    def upload(self):
        data = self.serialize()
        return self.api.put_skill_settings_v1(data)

    def upload_meta(self):
        self.api.upload_skill_metadata(self.meta)

    def load(self):
        if not isfile(self.local_path):
            self.settings = {}
        else:
            with open(self.local_path) as f:
                self.settings = json.load(f)

    def store(self):
        makedirs(dirname(self.local_path), exist_ok=True)
        with open(self.local_path, "w") as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key):
        return self.settings.get(key)

    def __str__(self):
        return str(self.settings)

    def __setitem__(self, key, value):
        self.settings[key] = value

    def __getitem__(self, item):
        return self.settings.get(item)

    def __dict__(self):
        return self.serialize()

    def serialize(self):
        meta = deepcopy(self.meta)
        for idx, section in enumerate(meta.get('sections', [])):
            for idx2, field in enumerate(section["fields"]):
                if "value" not in field:
                    continue
                if field["name"] in self.settings:
                    val = self.settings[field["name"]]
                    meta['sections'][idx]["fields"][idx2]["value"] = str(val)
        return {'skillMetadata': meta,
                "skill_gid": self.identifier,
                "display_name": get_display_name(self.skill_id)}

    def deserialize(self, data):
        if isinstance(data, str):
            data = json.loads(data)

        skill_json = {}
        skill_meta = data.get("skillMetadata") or {}
        for s in skill_meta.get("sections", []):
            for f in s.get("fields", []):
                if "name" in f and "value" in f:
                    val = f["value"]
                    if isinstance(val, str):
                        t = f.get("type", "")
                        if t == "checkbox":
                            if val.lower() == "true" or val == "1":
                                val = True
                            else:
                                val = False
                        elif t == "number":
                            val = float(val)
                        elif val.lower() in ["none", "null", "nan"]:
                            val = None
                        elif val == "[]":
                            val = []
                        elif val == "{}":
                            val = {}

                    skill_json[f["name"]] = val

        remote_id = data.get("skill_gid") or \
                    data.get("identifier")  # deprecated

        fields = remote_id.split("|")
        skill_id = fields[0]
        if len(fields) > 1 and fields[0].startswith("@"):
            skill_id = fields[1]
        return RemoteSkillSettings(skill_id, skill_json, skill_meta, remote_id=remote_id,
                                   url=self.api.backend_url, version=self.api.backend_version)

    def __enter__(self):
        self.load()
        self.download()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.generate_meta()
        self.upload()
        self.store()


class SeleneSkillsManifest(JsonStorage):
    """dict subclass with save/load support

    This dictionary contains the metadata expected by selene backend
    This data is used to populate entries in selene skill settings page

    """

    def __init__(self, api=None):
        path = os.path.join(get_xdg_data_save_path(), 'skills.json')
        super().__init__(path, disable_lock=True)
        if "skills" not in self:
            self["skills"] = []
            self.store()
        self.api = api or DeviceApi()

    @staticmethod
    def _get_default_skills_directory(conf=None):
        """ return default directory to scan for skills

        users can define the data directory in mycroft.conf
        the skills folder name (relative to data_dir) can also be defined there

        NOTE: folder name also impacts all XDG skill directories!

        {
            "data_dir": "/opt/mycroft",
            "skills": {
                "directory": "skills"
            }
        }

        Args:
            conf (dict): mycroft.conf dict, will be loaded automatically if None
        """
        conf = conf or Configuration()
        data_dir = conf.get("data_dir") or "/opt/mycroft"
        folder = conf["skills"].get("directory") or "skills"

        skills_folder = f"{data_dir}/{folder}"

        # create folder if needed
        try:
            makedirs(skills_folder, exist_ok=True)
        except PermissionError:  # old style /opt/mycroft/skills not available
            skills_folder = f"{get_xdg_data_save_path()}/{folder}"
            makedirs(skills_folder, exist_ok=True)

        return expanduser(skills_folder)

    @staticmethod
    def _get_skill_directories(conf=None):
        """ returns list of skill directories ordered by expected loading order

        This corresponds to:
        - XDG_DATA_DIRS
        - default directory (see get_default_skills_directory method for details)
        - user defined extra directories

        Each directory contains individual skill folders to be loaded

        If a skill exists in more than one directory (same folder name) previous instances will be ignored
            ie. directories at the end of the list have priority over earlier directories

        NOTE: empty folders are interpreted as disabled skills

        new directories can be defined in mycroft.conf by specifying a full path
        each extra directory is expected to contain individual skill folders to be loaded

        the xdg folder name can also be changed, it defaults to "skills"
            eg. ~/.local/share/mycroft/FOLDER_NAME

        {
            "skills": {
                "directory": "skills",
                "extra_directories": ["path/to/extra/dir/to/scan/for/skills"]
            }
        }

        Args:
            conf (dict): mycroft.conf dict, will be loaded automatically if None
        """
        # the contents of each skills directory must be individual skill folders
        # we are still dependent on the mycroft-core structure of skill_id/__init__.py

        conf = conf or Configuration()
        folder = conf["skills"].get("directory") or "skills"

        # load all valid XDG paths
        skill_locations = list(reversed(
            [os.path.join(p, folder) for p in get_xdg_data_dirs()]
        ))

        # load the default skills folder
        default = SeleneSkillsManifest._get_default_skills_directory(conf)
        if default not in skill_locations:
            skill_locations.append(default)

        # load additional explicitly configured directories
        conf = conf.get("skills") or {}
        # extra_directories is a list of directories containing skill subdirectories
        # NOT a list of individual skill folders
        skill_locations += conf.get("extra_directories") or []
        return skill_locations

    def device_skill_state_hash(self):
        return hash(json.dumps(self, sort_keys=True))

    def add_skill(self, skill_id):
        if self.api.identity.uuid:
            skill_gid = f'@{self.api.identity.uuid}|{skill_id}'
        else:
            skill_gid = f'@|{skill_id}'
        skill = {
            "name": skill_id,
            "origin": "non-msm",
            "beta": True,
            "status": 'active',
            "installed": 0,
            "updated": 0,
            "installation": 'installed',
            "skill_gid": skill_gid
        }
        if "skills" not in self:
            self["skills"] = []
        self["skills"].append(skill)

    def get_skill_state(self, skill_id):
        """Find a skill entry in the device skill state and returns it."""
        for skill_state in self.get('skills', []):
            if skill_state.get('name') == skill_id:
                return skill_state
        return {}

    def scan_skills(self, skill_dirs=None):
        # TODO - this should go into ovos_utils
        skill_dirs = skill_dirs or self._get_skill_directories()
        for directory in skill_dirs:
            if not isdir(directory):
                continue
            for skill_id in os.listdir(directory):
                skill_init = join(directory, skill_id, "__init__.py")
                if isfile(skill_init):
                    self.add_skill(skill_id)
        # TODO - plugin skills
        self.store()


if __name__ == "__main__":
    s = RemoteSkillSettings("mycroft-date-time")
    print(s.api.get_skill_settings_v1())
    s.download()
    print(s)
    s.settings["not"] = "yes"  # ignored, not in meta
    s.settings["show_time"] = True
    s.upload()
    s.download()
    print(s)
    s.settings["not"] = "yes"
    s.generate_meta()  # now in meta
    s.settings["not"] = "no"
    s.settings["show_time"] = False
    s.upload()
    s.download()
    print(s)
