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
from typing import Tuple


class PackageFormat:
    """
    Possible categories a package can be classified as
    This is used to guess name variants in different package managers
    """
    exe = 'exe'
    lib = 'lib'
    lib_dev = 'lib-dev'
    lib_debug = 'lib-debug'
    none = 'none'  # no special formatting

    all = [exe, lib, lib_dev, lib_debug, none]

    @classmethod
    def parse(cls, package_string: str) -> Tuple[str, str]:
        """
        Convert package name to base package name and package format string
        Example: 'libgdb-dev' -> ('gdb', 'lib-dev')
        """

        def try_parse(param, from_end=True):
            nonlocal package_string
            if from_end:
                if package_string.endswith(param):
                    package_string = package_string[:-len(param)]
                    return True
            else:
                if package_string.startswith(param):
                    package_string = package_string[len(param):]
                    return True

        has_lib = try_parse('lib', False)
        has_dev = (
                try_parse('-dev') or
                try_parse('-devel')
        )
        has_debug = (
                try_parse('-dbg') or
                try_parse('-debug') or
                try_parse('-dbginfo')
        )
        has_exe = (
                try_parse('-utils') or
                try_parse('-bin')
        )
        if has_dev:
            fmt = cls.lib_dev
        elif has_debug:
            fmt = cls.lib_debug
        elif has_lib:
            fmt = cls.lib
        elif has_exe:
            fmt = cls.exe
        else:
            fmt = cls.exe
        return package_string, fmt
