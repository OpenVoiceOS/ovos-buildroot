# Copyright (c) 2018 Mycroft AI, Inc.
#
# This file is part of Mycroft Skills Manager
# (see https://github.com/MycroftAI/mycroft-skills-manager).
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

import logging
import os
import yaml
from contextlib import contextmanager
from difflib import SequenceMatcher
from os.path import exists, join, basename
from threading import Lock
from typing import Callable

LOG = logging.getLogger(__name__)

# Branches which can be switched from when updating
# TODO Make this configurable
SWITCHABLE_BRANCHES = ['master']

# default constraints to use if no are given
DEFAULT_CONSTRAINTS = '/etc/mycroft/constraints.txt'
FIVE_MINUTES = 300


def _perform_pako_install(packages, system_packages=None):
    pass


@contextmanager
def work_dir(directory):
    old_dir = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(old_dir)


def _backup_previous_version(func: Callable = None):
    return func


class SkillEntry:
    pip_lock = Lock()
    manifest_yml_format = {
        'dependencies': {
            'system': {},
            'exes': [],
            'skill': [],
            'python': []
        }
    }

    def __init__(self, name, path, url='', sha='', msm=None):
        url = url.rstrip('/')
        url = url[:-len('.git')] if url.endswith('.git') else url
        self.path = path
        self.url = url
        self.sha = sha
        self.msm = msm
        if msm:
            u = url.lower()
            self.meta_info = msm.repo.skills_meta_info.get(u, {})
        else:
            self.meta_info = {}
        if name is not None:
            self.name = name
        elif 'name' in self.meta_info:
            self.name = self.meta_info['name']
        else:
            self.name = basename(path)

        # TODO: Handle git:// urls as well
        from_github = False
        if url.startswith('https://'):
            url_tokens = url.rstrip("/").split("/")
            from_github = url_tokens[-3] == 'github.com' if url else False
        self.author = self.extract_author(url) if from_github else ''
        self.id = self.extract_repo_id(url) if from_github else self.name
        self.is_local = exists(path)
        self.old_path = None  # Path of previous version while upgrading

    @property
    def is_beta(self):
        return True

    @property
    def is_dirty(self):
        return False

    @property
    def skill_gid(self):
        """Format skill gid for the skill.

        This property does some Git gymnastics to determine its return value.
        When a device boots, each skill accesses this property several times.
        To reduce the amount of boot time, cache the value returned by this
        property.  Cache expires five minutes after it is generated.
        """
        LOG.debug('Generating skill_gid for ' + self.name)
        gid = ''
        if self.is_dirty:
            gid += '@|'
        if self.meta_info != {}:
            gid += self.meta_info['skill_gid']
        else:
            name = self.name.split('.')[0]
            gid += name
        return gid

    def __str__(self):
        return self.name

    def attach(self, remote_entry):
        """Attach a remote entry to a local entry"""
        return self

    @classmethod
    def from_folder(cls, path, msm=None, use_cache=True):
        """Find or create skill entry from folder path.

        Arguments:
            path:       path of skill folder
            msm:        mock_msm instance to use for caching and extended information
                        retrieval.
            use_cache:  Enable/Disable cache usage. defaults to True
        """
        if msm and use_cache:
            skills = {skill.path: skill for skill in msm.local_skills.values()}
            if path in skills:
                return skills[path]
        return cls(None, path, cls.find_git_url(path), msm=msm)

    @classmethod
    def create_path(cls, folder, url, name=''):
        return join(folder, '{}.{}'.format(
            name or cls.extract_repo_name(url), cls.extract_author(url)
        ).lower())

    @staticmethod
    def extract_repo_name(url):
        s = url.rstrip('/').split("/")[-1]
        a, b, c = s.rpartition('.git')
        if not c:
            return a
        return s

    @staticmethod
    def extract_author(url):
        return url.rstrip('/').split("/")[-2].split(':')[-1]

    @classmethod
    def extract_repo_id(cls, url):
        return '{}:{}'.format(cls.extract_author(url).lower(),
                              cls.extract_repo_name(url)).lower()

    @staticmethod
    def _tokenize(x):
        return x.replace('-', ' ').split()

    @staticmethod
    def _extract_tokens(s, tokens):
        s = s.lower().replace('-', ' ')
        extracted = []
        for token in tokens:
            extracted += [token] * s.count(token)
            s = s.replace(token, '')
        s = ' '.join(i for i in s.split(' ') if i)
        tokens = [i for i in s.split(' ') if i]
        return s, tokens, extracted

    @classmethod
    def _compare(cls, a, b):
        return SequenceMatcher(a=a, b=b).ratio()

    def match(self, query, author=None):
        search, search_tokens, search_common = self._extract_tokens(
            query, ['skill', 'fallback', 'mycroft']
        )

        name, name_tokens, name_common = self._extract_tokens(
            self.name, ['skill', 'fallback', 'mycroft']
        )

        weights = [
            (9, self._compare(name, search)),
            (9, self._compare(name.split(' '), search_tokens)),
            (2, self._compare(name_common, search_common)),
        ]
        if author:
            author_weight = self._compare(self.author, author)
            weights.append((5, author_weight))
            author_weight = author_weight
        else:
            author_weight = 1.0
        return author_weight * (
            sum(weight * val for weight, val in weights) /
            sum(weight for weight, val in weights)
        )

    def run_pip(self, constraints=None):
        return False

    def install_system_deps(self):
        return False

    def run_requirements_sh(self):
        return False

    def run_skill_requirements(self):
        return False

    def verify_info(self, info, fmt):
        pass

    def skill_info(self):
        yml_path = join(self.path, 'manifest.yml')
        if exists(yml_path):
            LOG.info('Reading from manifest.yml')
            with open(yml_path) as f:
                info = yaml.safe_load(f)
                self.verify_info(info, self.manifest_yml_format)
                return info or {}
        return {}

    def dependencies(self):
        return self.skill_info.get('dependencies') or {}

    def dependent_skills(self):
        skills = set()
        reqs = join(self.path, "skill_requirements.txt")
        if exists(reqs):
            with open(reqs, "r") as f:
                for i in f.readlines():
                    skill = i.strip()
                    if skill:
                        skills.add(skill)
        for i in self.dependencies.get('skill') or []:
            skills.add(i)
        return list(skills)

    def dependent_python_packages(self):
        reqs = join(self.path, "requirements.txt")
        req_lines = []
        if exists(reqs):
            with open(reqs, "r") as f:
                req_lines += f.readlines()
        req_lines += self.dependencies.get('python') or []
        # Strip comments
        req_lines = [line.split('#')[0].strip() for line in req_lines]
        return [line for line in req_lines if line]  # Strip empty lines

    def dependent_system_packages(self):
        return self.dependencies.get('system') or {}

    def remove(self):
        raise NotImplementedError

    def install(self, constraints=None):
        raise NotImplementedError

    def update_deps(self, constraints=None):
        raise NotImplementedError

    def _find_sha_branch(self):
        return ""

    def update(self):
        return False

    @staticmethod
    def find_git_url(path):
        return ''

    def __repr__(self):
        return '<SkillEntry {}>'.format(' '.join(
            '{}={}'.format(attr, self.__dict__[attr])
            for attr in ['name', 'author', 'is_local']
        ))
