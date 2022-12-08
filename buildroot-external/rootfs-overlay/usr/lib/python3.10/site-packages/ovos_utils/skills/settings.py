import requests
import json
from os.path import join, expanduser, exists
from json_database import JsonStorageXDG, JsonStorage
from ovos_utils.log import LOG


def settings2meta(settings, section_name="Skill Settings"):
    """ generates basic settingsmeta """
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
        if isinstance(v, int):
            fields.append({
                "name": k,
                "type": "number",
                "label": label,
                "value": str(v)
            })
    return {
        "skillMetadata": {
            "sections": [
                {
                    "name": section_name,
                    "fields": fields
                }
            ]
        }
    }


class PrivateSettings(JsonStorageXDG):
    def __init__(self, skill_id):
        super(PrivateSettings, self).__init__(skill_id)

    @property
    def settingsmeta(self):
        return settings2meta(self, self.name)


def get_remote_settings(skill_id, identity_file=None, backend_url=None):
    """ WARNING: selene backend does not use proper skill_id, if you have
    skills with same name but different author settings will overwrite each
    other on the backend, THIS METHOD IS NOT SAFE

    skill matching is currently done by checking "if {skill} in string"
    once mycroft fixes it on their side this will start using a proper
    unique identifier
    """
    data = get_all_remote_settings(identity_file, backend_url)
    for k, v in data.items():
        if skill_id in k:
            return v or {}
    return data


def get_all_remote_settings(identity_file=None, backend_url=None):
    """ WARNING: selene backend does not use proper skill_id, if you have
    skills with same name but different author settings will overwrite each
    other on the backend, THIS METHOD IS NOT SAFE
    """
    backend_url = backend_url or "https://api.mycroft.ai"
    identity_file = identity_file or expanduser(
        join("~", ".mycroft", "identity", "identity2.json"))
    if not exists(identity_file):
        return {}
    with open(identity_file) as f:
        identity = json.load(f)
    url = backend_url + "/v1/device/" + identity["uuid"] + "/skill/settings"
    params = {"Authorization": "Bearer " + identity["access"],
              "Content-Type": "application/json"
              }
    return requests.get(url, headers=params).json()


def get_local_settings(skill_dir, skill_name=None) -> dict:
    """Build a JsonStorage using the JSON string stored in settings.json."""
    if skill_name:
        LOG.warning("skill_name is an unused legacy argument, will be removed in 0.0.3 or later")
    if skill_dir.endswith("/settings.json"):
        settings_path = skill_dir
    else:
        settings_path = join(skill_dir, 'settings.json')
    LOG.info(settings_path)
    return JsonStorage(settings_path)


def save_settings(skill_dir, skill_settings):
    """Save skill settings to file."""
    if skill_dir.endswith("/settings.json"):
        settings_path = skill_dir
    else:
        settings_path = join(skill_dir, 'settings.json')

    settings = JsonStorage(settings_path)
    for k, v in skill_settings.items():
        settings[k] = v
    try:
        settings.store()
    except Exception:
        LOG.error(f'error saving skill settings to {settings_path}')
    else:
        LOG.info(f'Skill settings successfully saved to {settings_path}')