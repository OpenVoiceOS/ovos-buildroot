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
from glob import glob
from os.path import join, basename
from xdg import BaseDirectory
import logging

LOG = logging.getLogger(__name__)

MYCROFT_SKILLS_DATA = ("https://raw.githubusercontent.com/"
                       "MycroftAI/mycroft-skills-data")
FIVE_MINUTES = 300


def download_skills_data(branch, path):
    return {}


def load_cached_skills_data(path):
    return {}


def load_skills_data(branch, path):
    return {}


class SkillRepo:
    def __init__(self, url=None, branch=None):
        self.path = join(BaseDirectory.save_data_path('mycroft'),
                         'skills-repo')
        self.url = url or "https://github.com/MycroftAI/mycroft-skills"
        self.branch = branch or "20.08"
        self.repo_info = {}

    @property
    def skills_meta_info(self):
        return {}

    def read_file(self, filename):
        with open(join(self.path, filename)) as f:
            return f.read()

    def __prepare_repo(self):
        pass

    def update(self):
        pass

    def get_skill_data(self):
        """ generates tuples of name, path, url, sha """
        for name, path, url, sha in []:
            yield name, path, url, sha

    def get_shas(self):
        for folder, sha in []:
            yield folder, sha

    def get_default_skill_names(self):
        for defaults_file in glob(join(self.path, 'DEFAULT-SKILLS*')):
            with open(defaults_file) as f:
                skills = list(filter(
                    lambda x: x and not x.startswith('#'),
                    map(str.strip, f.read().split('\n'))
                ))
            platform = basename(defaults_file).replace('DEFAULT-SKILLS', '')
            platform = platform.replace('.', '') or 'default'
            yield platform, skills
