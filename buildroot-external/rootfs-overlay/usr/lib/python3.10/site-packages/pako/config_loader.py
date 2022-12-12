# Copyright (c) 2019 Mycroft AI, Inc.
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
import appdirs
import json
import tempfile
from logging import getLogger
from os.path import join, isfile, isdir, dirname
from subprocess import call


def recursive_merge(a, b):
    """Returns a generator for the merged dict of a and b"""
    for k in set(a.keys()) | set(b.keys()):
        if k in a and k in b:
            if isinstance(a[k], dict) and isinstance(b[k], dict):
                yield k, dict(recursive_merge(a[k], b[k]))
            else:
                yield k, b[k]
        elif k in a:
            yield k, a[k]
        else:
            yield k, b[k]


def get_config_filename():
    return join(appdirs.site_config_dir('pako'), 'pako.conf')


def try_write_empty_config_stub():
    config_file = get_config_filename()
    if not isfile(config_file):
        from pako.package_manager_data import get_package_manager_names

        config_dir = dirname(config_file)
        if not isdir(config_dir):
            call(['sudo', 'mkdir', config_dir])

        fd, path = tempfile.mkstemp()
        with open(fd, 'w') as temp:
            base = {i: {} for i in get_package_manager_names()}
            base['__order__'] = []
            json.dump(base, temp, indent=4)
        call(['sudo', 'mv', path, config_file])


def load_package_managers_overrides() -> dict:
    """Load the optional package manager data overrides from disk"""
    config_file = get_config_filename()
    try:
        with open(config_file) as f:
            return json.load(f)
    except ValueError:
        getLogger(__name__).warning('Failed to load config file')
        return {}
    except OSError:
        return {}
