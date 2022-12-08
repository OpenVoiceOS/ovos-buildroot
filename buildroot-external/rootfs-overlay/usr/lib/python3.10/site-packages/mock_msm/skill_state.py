"""Functions related to manipulating the skills.json file."""
import json
from logging import getLogger
from os.path import join

from xdg import BaseDirectory

LOG = getLogger(__name__)


def get_state_path():
    """Get complete path for skill state file.

    Returns:
        (str) path to skills.json
    """
    return join(BaseDirectory.save_data_path('mycroft'), 'skills.json')


def load_device_skill_state() -> dict:
    return {}


def write_device_skill_state(data: dict):
    pass


def get_skill_state(name, device_skill_state) -> dict:
    return {}


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
