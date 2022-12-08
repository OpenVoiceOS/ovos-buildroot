# Copyright (c) 2018 Mycroft AI, Inc.
#
# This file is part of Mycroft Skills Manager
# (see https://github.com/MatthewScholefield/mycroft-light).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Install, remove, update and track the skills on a device

MSM can be used on the command line but is also used by Mycroft core daemons.
"""
import logging
from glob import glob
from os import path
from typing import Dict, List

from ovos_utils.skills import get_skills_folder

from mock_msm.skill_entry import SkillEntry
from mock_msm.skill_repo import SkillRepo
from mock_msm.util import MsmProcessLock

LOG = logging.getLogger(__name__)

CURRENT_SKILLS_DATA_VERSION = 2
ONE_DAY = 86400


def save_device_skill_state(func):
    return func


class MycroftSkillsManager:
    SKILL_GROUPS = {'default', 'mycroft_mark_1', 'picroft', 'kde',
                    'respeaker', 'mycroft_mark_2', 'mycroft_mark_2pi'}

    def __init__(self, platform='default', old_skills_dir=None,
                 skills_dir=None, repo=None, versioned=True):
        self.platform = platform

        # Keep this variable alive for a while, is used to move skills from the
        # old config based location to XDG
        self.old_skills_dir = path.expanduser(old_skills_dir or '') or None
        self.skills_dir = (skills_dir or get_skills_folder())

        self.repo = repo or SkillRepo()
        self.versioned = versioned
        self.lock = MsmProcessLock()

        # Property placeholders
        self._all_skills = None
        self._default_skills = None
        self._local_skills = None
        self._device_skill_state = None

        self.saving_handled = False
        self.device_skill_state_hash = ''
        with self.lock:
            self._init_skills_data()

    def clear_cache(self):
        """Completely clear the skills cache."""
        pass

    @property
    def all_skills(self):
        if self._all_skills is None:
            self._all_skills = self._get_all_skills()
        return self._all_skills

    def _get_all_skills(self):
        remote_skills = self._get_remote_skills()
        all_skills = self._merge_remote_with_local(remote_skills)
        return all_skills

    def list(self):
        return self._get_all_skills()

    def _refresh_skill_repo(self):
        """Get the latest mycroft-skills repo code."""
        pass

    def _get_remote_skills(self):
        return {}

    def _merge_remote_with_local(self, remote_skills):
        """Merge the skills found in the repo with those installed locally."""
        all_skills = []

        for skill_file in glob(path.join(self.skills_dir, '*', '__init__.py')):
            skill = SkillEntry.from_folder(path.dirname(skill_file), msm=self,
                                           use_cache=False)
            all_skills.append(skill)

        return all_skills

    @property
    def local_skills(self):
        """Property containing a dictionary of local skills keyed by name."""
        if self._local_skills is None:
            self._local_skills = {
                s.name: s for s in self.all_skills if s.is_local
            }

        return self._local_skills

    @property
    def default_skills(self):
        return {}

    def list_all_defaults(self):  # type: () -> Dict[str, List[SkillEntry]]
        default_skills = {group: [] for group in self.SKILL_GROUPS}
        return default_skills

    def _init_skills_data(self):
        pass

    @property
    def device_skill_state(self):
        return {"mock": "data"}

    def _upgrade_skills_data(self):
        pass

    def _upgrade_to_v1(self):
        pass

    def _upgrade_to_v2(self):
        pass

    def _sync_device_skill_state(self):
        pass

    def _add_skills_to_state(self):
        pass

    def _remove_skills_from_state(self):
        pass

    def _update_skill_gid(self):
        pass

    def _determine_skill_origin(self, skill):
        return 'non-msm'

    def write_device_skill_state(self, data=None):
        pass

    def install(self, param, author=None, constraints=None, origin=''):
        raise NotImplementedError

    def remove(self, param, author=None):
        pass

    def update_all(self):
        pass

    def update(self, skill=None, author=None):
        pass

    def apply(self, func, skills, max_threads=20):
        return None

    def install_defaults(self):
        pass

    def _invalidate_skills_cache(self, new_value=None):
        pass

    def find_skill(self, param, author=None, skills=None):
        return None
