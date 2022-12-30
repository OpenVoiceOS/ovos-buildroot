# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import re
import importlib.util
from typing import Tuple, Optional

import pkg_resources
import sysconfig

from os.path import exists, join, expanduser, isdir
from neon_utils.logger import LOG


def parse_version_string(ver: str) -> Tuple[int, int, int, Optional[int]]:
    """
    Parse a semver string into its component versions as ints
    :param ver: Version string to parse
    :returns: Tuple major, minor, patch, Optional(revision)
    """
    parts = ver.split('.')
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = parts[2] if len(parts) > 2 else '0'
    if not patch.isnumeric():
        patch, alpha = re.split(r"\D+", patch, 1)
        alpha = int(alpha)
    else:
        alpha = None
    patch = int(patch)
    return major, minor, patch, alpha


def get_package_version_spec(pkg: str):
    """
    Locate an installed package and return its reported version
    :param pkg: string package name to locate
    :returns: Version string as reported by pkg_resources
    :raises: ModuleNotFoundError if requested package isn't installed
    """
    try:
        return pkg_resources.get_distribution(pkg).version
    except pkg_resources.DistributionNotFound:
        raise ModuleNotFoundError(f"{pkg} not found")


def get_package_dependencies(pkg: str):
    """
    Get the dependencies for an installed package
    :param pkg: string package name to evaluate
    :returns: list of string dependencies (equivalent to requirements.txt)
    :raises ModuleNotFoundError if requested package isn't installed
    """
    try:
        constraints = pkg_resources.working_set.by_key[pkg].requires()
        constraints_spec = [str(c).split('[', 1)[0] for c in constraints]
        LOG.debug(constraints_spec)
        return constraints_spec
    except KeyError:
        raise ModuleNotFoundError(f"{pkg} not found")


def get_packaged_core_version() -> str:
    """
    Get the version of the packaged core in use.
    Supports Neon, Mycroft, and OVOS default packages.
    Returns:
        Version of the installed core package
    """
    if importlib.util.find_spec("neon-core"):
        return get_package_version_spec("neon-core")
    elif importlib.util.find_spec("mycroft-core"):
        return get_package_version_spec("mycroft-core")
    elif importlib.util.find_spec("mycroft-lib"):
        return get_package_version_spec("mycroft-lib")
    raise ImportError("No Core Package Found")


def get_neon_core_version() -> str:
    """
    Gets the current version of the installed Neon Core.
    Returns:
        Version of the available/active Neon Core or
        0.0 if no release info is found
    """
    try:
        return get_packaged_core_version()
    except ImportError:
        pass

    return "0.0"


def get_core_root():
    """
    Depreciated 2020.09.01
    :return:
    """
    LOG.warning(f"This method is depreciated, "
                f"please update to use get_neon_core_root()")
    return get_mycroft_core_root()


def get_neon_core_root():
    """
    Determines the root of the available/active Neon Core.
    Directory returned is the root of the `neon_core` package
    Returns:
        Path to the 'neon_core' directory
    """
    site = sysconfig.get_paths()['platlib']
    if exists(join(site, 'neon_core')):
        return join(site, 'neon_core')
    for p in [path for path in sys.path if path != ""]:
        if exists(join(p, "neon_core")):
            return join(p, "neon_core")
        if re.match(".*/lib/python.*/site-packages", p):
            clean_path = "/".join(p.split("/")[0:-4])
            if exists(join(clean_path, "neon_core")):
                return join(clean_path, "neon_core")
            elif exists(join(p, "neon_core")):
                return join(p, "neon_core")
    raise FileNotFoundError("Could not determine core directory")


def get_mycroft_core_root():
    """
    Determines the root of the available/active Neon Core.
    Should be the immediate parent directory of 'mycroft' dir
    Returns:
        Path to the core directory containing 'mycroft'
    """
    site = sysconfig.get_paths()['platlib']
    if exists(join(site, 'mycroft')):
        return site
    for p in [path for path in sys.path if path != ""]:
        if exists(join(p, "mycroft")):
            return p
        if re.match(".*/lib/python.*/site-packages", p):
            clean_path = "/".join(p.split("/")[0:-4])
            if exists(join(clean_path, "mycroft")):
                return clean_path
            # TODO: Other packages (Neon Core)? DM
            elif exists(join(p, "mycroft")):
                return p
    raise FileNotFoundError("Could not determine core directory")


def build_skill_spec(skill_dir: str) -> dict:
    """
    Build dict contents of a skill.json file.
    :param skill_dir: path to skill directory to parse
    :returns: dict skill.json spec
    """
    import shutil
    from ovos_skills_manager.local_skill import get_skill_data_from_directory
    from neon_utils.file_utils import parse_skill_readme_file
    from neon_utils.configuration_utils import dict_merge

    def get_skill_license():  # TODO: Implement OSM version of this
        try:
            with open(join(skill_dir, "LICENSE.md")) as f:
                contents = f.read()
        except FileNotFoundError:
            return "Unknown"
        except Exception as e:
            LOG.error(e)
            return "Unknown"
        if "BSD-3" in contents:
            return "BSD-3-Clause"
        if "Apache License" in contents:
            return "Apache 2.0"
        if "Neon AI Non-commercial Friendly License 2.0" in contents:
            return "Neon 2.0"
        if "Neon AI Non-commercial Friendly License" in contents:
            return "Neon 1.0"

    _invalid_skill_data_keys = ("appstore", "appstore_url", "credits",
                                "skill_id")
    _invalid_readme_keys = ("contact support", "details")
    default_skill = {"title": "",
                     "url": "",
                     "summary": "",
                     "short_description": "",
                     "description": "",
                     "examples": [],
                     "desktopFile": False,
                     "warning": "",
                     "systemDeps": False,
                     "requirements": {
                         "python": [],
                         "system": {},
                         "skill": []
                     },
                     "incompatible_skills": [],
                     "platforms": ["i386",
                                   "x86_64",
                                   "ia64",
                                   "arm64",
                                   "arm"],
                     "branch": "master",
                     "license": "",
                     "icon": "",
                     "category": "",
                     "categories": [],
                     "tags": [],
                     "credits": [],
                     "skillname": "",
                     "authorname": "",
                     "foldername": None}

    skill_dir = expanduser(skill_dir)
    if not isdir(skill_dir):
        raise FileNotFoundError(f"Not a Directory: {skill_dir}")
    LOG.debug(f"skill_dir={skill_dir}")
    skill_json = join(skill_dir, "skill.json")
    backup = join(skill_dir, "skill_json.bak")
    shutil.move(skill_json, backup)
    skill_data = get_skill_data_from_directory(skill_dir)
    shutil.move(backup, skill_json)
    skill_data['foldername'] = None
    for key in _invalid_skill_data_keys:
        if key in skill_data:
            skill_data.pop(key)
    readme_data = parse_skill_readme_file(join(skill_dir, "README.md"))
    for key in _invalid_readme_keys:
        if key in readme_data:
            readme_data.pop(key)
    readme_data["short_description"] = readme_data.get("summary")
    readme_data["license"] = get_skill_license()
    readme_data["branch"] = "master"
    skill_data = dict_merge(default_skill, skill_data)
    skill_data["requirements"]["python"].sort()
    return dict(dict_merge(skill_data, readme_data))
