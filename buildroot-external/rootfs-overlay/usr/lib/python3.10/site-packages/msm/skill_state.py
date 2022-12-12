"""Functions related to manipulating the skills.json file."""
import json
import shutil
from logging import getLogger
from os import makedirs
from os.path import isfile, dirname, join, expanduser

from xdg import BaseDirectory

LOG = getLogger(__name__)


def get_state_path():
    """Get complete path for skill state file.

    Returns:
        (str) path to skills.json
    """
    return join(BaseDirectory.save_data_path('mycroft'), 'skills.json')


# Make sure we migrate the installed skills file from the old non-XDG location
old_skill_state_path = expanduser('~/.mycroft/skills.json')
if isfile(old_skill_state_path):
    shutil.move(old_skill_state_path, get_state_path())


def load_device_skill_state() -> dict:
    """Contains info on how skills should be updated"""
    skills_data_path = get_state_path()
    device_skill_state = {}
    if isfile(skills_data_path):
        try:
            with open(skills_data_path) as skill_state_file:
                device_skill_state = json.load(skill_state_file)
        except json.JSONDecodeError:
            LOG.exception('failed to load skills.json')

    return device_skill_state


def write_device_skill_state(data: dict):
    """Write the device skill state to disk."""
    dir_path = dirname(get_state_path())
    try:
        # create folder if it does not exist
        makedirs(dir_path)
    except Exception:
        pass
    skill_state_path = get_state_path()
    with open(skill_state_path, 'w') as skill_state_file:
        json.dump(data, skill_state_file, indent=4, separators=(',', ':'))


def get_skill_state(name, device_skill_state) -> dict:
    """Find a skill entry in the device skill state and returns it."""
    skill_state_return = {}
    for skill_state in device_skill_state.get('skills', []):
        if skill_state.get('name') == name:
            skill_state_return = skill_state

    return skill_state_return


def initialize_skill_state(name, origin, beta, skill_gid) -> dict:
    """Create a new skill entry

    Arguments:
        name: skill name
        origin: the source of the installation
        beta: Boolean indicating wether the skill is in beta
        skill_gid: skill global id
    Returns:
        populated skills entry
    """
    return dict(
        name=name,
        origin=origin,
        beta=beta,
        status='active',
        installed=0,
        updated=0,
        installation='installed',
        skill_gid=skill_gid
    )


def device_skill_state_hash(data):
    return hash(json.dumps(data, sort_keys=True))
