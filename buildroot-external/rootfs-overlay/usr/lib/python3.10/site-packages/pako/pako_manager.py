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
import sys

from os.path import basename
from shutil import which
from subprocess import call, PIPE

from pako.config_loader import try_write_empty_config_stub
from pako.package_format import PackageFormat
from pako.package_manager_data import load_package_manager_data


class PakoManager:
    def __init__(self):
        self.has_sudo = False
        self.all_data = load_package_manager_data()
        self.name = self._find_package_manager(list(self.all_data))

        if not self.name:
            raise RuntimeError('Package manager not found!')

        self.exe = which(self.name)
        self.config = self.all_data[self.name]
        if self.config['sudo'] and not sys.stdout.isatty() and not self._check_for_sudo():
            raise RuntimeError('Sudo required (and script not launched interactively)')

    def _check_for_sudo(self):
        return call(['sudo', '-n', 'true'], stderr=PIPE) == 0

    @staticmethod
    def _find_package_manager(exes):
        """Determine which package manager exists on a system."""
        for exe in exes:
            if which(exe):
                return exe
        return None

    def call(self, args: list):
        """Execute command for the available package manager.
        
        Arguments:
            args (List): list of command line arguments use
        """
        sudo_args = []
        if self.config['sudo']:
            sudo_args = ['sudo']
            if not self.has_sudo:
                if not self._check_for_sudo():
                    print('Requesting sudo to run command: {}...'.format(
                        ' '.join([basename(self.exe)] + args)
                    ))
        status = call(sudo_args + [self.exe] + args)
        self.has_sudo = self.config['sudo']
        if self.has_sudo:
            try_write_empty_config_stub()
        return status

    def update(self):
        """Update list of available packages."""
        return self.call(self.config['update'].split()) == 0

    def install_one(self, package: str, fmt: str = None, flags: list = []) -> bool:
        """Install a single system package.

        Arguments:
            package (Str): Name of package to install
            fmt (Str): Format of package name to use
            flags (List[Str]): A list of command flags to use if available
        Returns:
            Bool: True if package was successfully installed
        """
        if not fmt:
            package, fmt = PackageFormat.parse(package)
        if fmt not in PackageFormat.all:
            raise ValueError('Invalid package format: {}. Should be one of: {}'.format(
                fmt, PackageFormat.all
            ))

        possible_names = []
        for format_name, formats in self.config['formats'].items():
            if not fmt or format_name == fmt:
                for f in formats:
                    if f not in possible_names:
                        possible_names.append(f)

        install_cmd = self.config['install'].split()
        if 'no-confirm' in flags:
            install_cmd.append(self.config.get('flags').get('no-confirm'))
        for name in possible_names:
            if self.call(install_cmd + [name.format(package)]) == 0:
                return True
        return False

    def install(self, packages: list, overrides: dict = None, flags: list = []) -> bool:
        """Install system packages.

        Arguments:
            packages (List[Str]): A list of package names to install
            overrides (Dict): A dictionary of package name formats to use
            flags (List[Str]): A list of command flags to use if available
        Returns:
            Bool: True if all packages were successfully installed
        """
        if isinstance(packages, str):  # Easy mistake
            raise TypeError('Packages parameter must be a list')
        overrides = overrides or {}
        if self.name in overrides:
            packages = overrides[self.name]
            install_cmd = self.config['install'].split()
            if 'no-confirm' in flags:
                install_cmd.append(self.config.get('flags').get('no-confirm'))
            return self.call(install_cmd + packages) == 0
        for package in packages:
            if not self.install_one(package, flags=flags):
                return False
        return True
