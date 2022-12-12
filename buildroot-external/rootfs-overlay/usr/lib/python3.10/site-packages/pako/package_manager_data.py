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
from collections import OrderedDict

from pako.config_loader import recursive_merge, load_package_managers_overrides

__package_managers = {
    '__order__': ['eopkg', 'apt-get', 'rpm-ostree', 'dnf', 'pacman', 'yum', 'zypper', 'apk'],
    'eopkg': {
        'sudo': True,
        'update': 'ur',
        'install': 'it',
        'flags': {
            'no-confirm': '-y',
        },
        'formats': {
            'exe': ['{}', '{}-utils', '{}-bin'],
            'lib': ['{}', 'lib{}'],
            'lib-dev': ['{}-devel', 'lib{}-devel'],
            'lib-debug': ['{}-dbginfo', 'lib{}-dbginfo'],
        }
    },
    'apt-get': {
        'sudo': True,
        'update': 'update',
        'install': 'install',
        'flags': {
            'no-confirm': '-y',
        },
        'formats': {
            'exe': ['{}', '{}-utils'],
            'lib': ['lib{}', '{}'],
            'lib-dev': ['lib{}-dev', '{}-dev'],
            'lib-debug': ['lib{}-dbg', '{}-dbg']
        }
    },
    'rpm-ostree': {
        'sudo': False,
        'update': 'refresh-md',
        'install': 'install',
        'formats': {
            'exe': ['{}', '{}-utils'],
            'lib': ['{}', 'lib{}', '{}-lib', '{}-libs'],
            'lib-dev': ['{}-devel', 'lib{}-devel'],
            'lib-debug': ['{}-debuginfo', 'lib{}-debuginfo'],
        }
    },
    'dnf': {
        'sudo': True,
        'update': 'check-update',
        'install': 'install',
        'formats': {
            'exe': ['{}', '{}-utils'],
            'lib': ['{}', 'lib{}', '{}-lib', '{}-libs'],
            'lib-dev': ['{}-devel', 'lib{}-devel'],
            'lib-debug': ['{}-debuginfo', 'lib{}-debuginfo'],
        }
    },
    'pacman': {
        'sudo': True,
        'update': 'Syu',
        'install': 'Sy',
        'flags': {
            'no-confirm': '--noconfirm',
        },
        'formats': {
            'exe': ['{}', '{}-utils', '{}utils', '{}-bin'],
            'lib': ['{}', 'lib{}', '{}-lib', '{}-libs'],
            'lib-dev': [''],
            'lib-debug': ['{}-debug'],
        }
    },
    'yum': {
        'sudo': True,
        'update': 'update',
        'install': 'install',
        'flags': {
            'no-confirm': '-y',
        },
        'formats': {
            'exe': ['{}', '{}-utils', '{}utils', '{}-bin'],
            'lib': ['{}', 'lib{}', '{}-lib', '{}-libs'],
            'lib-dev': ['{}-devel'],
            'lib-debug': ['{}-debug','{}-dbg'],
        }
    },
    'zypper': {
        'sudo': True,
        'update': 'update',
        'install': 'install',
        'flags': {
            'no-confirm': '-y',
        },
        'formats': {
            'exe': ['{}', '{}-utils', '{}utils', '{}-bin'],
            'lib': ['{}', 'lib{}', '{}-lib', '{}-libs'],
            'lib-dev': ['{}-devel'],
            'lib-debug': ['{}-debug','{}-dbg'],
        }
    },
    'apk': {
        'sudo': True,
        'update': 'upgrade -a',
        'install': 'add',
        'formats': {
            'exe': ['{}', '{}-utils', '{}-progs', '{}-tools'],
            'lib': ['{}', 'lib{}', '{}-libs'],
            'lib-dev': ['{}-dev'],
            'lib-debug': ['{}-dbg'],
        }
    }
}


def get_package_manager_names():
    return list(__package_managers)


def load_package_manager_data():
    a = __package_managers
    b = load_package_managers_overrides()
    order = []
    order += [i for i in b.pop('__order__', []) if i not in order]
    order += [i for i in a.pop('__order__', []) if i not in order]
    data = dict(recursive_merge(a, b))
    order += [i for i in data if i not in order]
    return OrderedDict((k, data[k]) for k in order)
