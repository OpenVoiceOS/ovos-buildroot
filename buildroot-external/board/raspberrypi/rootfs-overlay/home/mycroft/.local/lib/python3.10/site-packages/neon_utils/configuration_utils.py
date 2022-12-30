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

import importlib
import re
import json
import os
import sys
import shutil
from time import sleep

import yaml

from copy import deepcopy
from os.path import *
from collections.abc import MutableMapping
from contextlib import suppress

from ovos_utils.json_helper import load_commented_json
from ovos_utils.xdg_utils import xdg_config_home
from typing import Optional
from combo_lock import NamedLock

from neon_utils.logger import LOG
from neon_utils.authentication_utils import find_neon_git_token, \
    build_new_auth_config
from neon_utils.file_utils import path_is_read_writable, create_file
from neon_utils.packaging_utils import get_package_version_spec


class NGIConfig:
    configuration_list = dict()
    # configuration_locks = dict()

    def __init__(self, name, path=None, force_reload: bool = False):
        self.name = name
        self.path = path or get_config_dir()
        lock_filename = join(self.path, f".{self.name}.lock")
        self.lock = NamedLock(lock_filename)
        self._pending_write = False
        self._content = dict()
        self._loaded = os.path.getmtime(self.file_path)
        if not force_reload and self.__repr__() in NGIConfig.configuration_list:
            cache = NGIConfig.configuration_list[self.__repr__()]
            cache.check_reload()
            self._content = cache.content
        else:
            with self.lock:
                self._content = self._load_yaml_file()
            NGIConfig.configuration_list[self.__repr__()] = self
        self._disk_content_hash = hash(repr(self._content))

    @property
    def file_path(self):
        """
        Returns the path to the yml file associated with this configuration
        Returns: path to this configuration yml
        """
        file_path = join(self.path, self.name + ".yml")
        if not isfile(file_path):
            if path_is_read_writable(self.path):
                create_file(file_path)
                LOG.debug(f"New YAML created: {file_path}")
            else:
                raise PermissionError(f"Cannot write to path: {self.path}")
        return file_path

    @property
    def requires_reload(self) -> bool:
        """
        Checks if yml file on disk has been modified since this config instance was last updated
        :returns: True if yml modified time is different than at last update
        """
        return self._loaded != os.path.getmtime(self.file_path)

    def check_reload(self):
        """
        Conditionally calls `self.check_for_updates` if `self.requires_reload` returns True.
        """
        if self.requires_reload:
            self.check_for_updates()

    def write_changes(self) -> bool:
        """
        Writes any changes to disk. If disk contents have changed, this config object will not modify config files
        :return: True if changes were written, False if disk config has been updated.
        """
        # TODO: Add some param to force overwrite? DM
        if self._pending_write or self._disk_content_hash != hash(repr(self._content)):
            return self._write_yaml_file()

    def populate(self, content, check_existing=False):
        if not check_existing:
            self.__add__(content)
            return
        old_content = deepcopy(self._content)
        self._content = dict_merge(content, self._content)  # to_change, one_with_all_keys
        if old_content == self._content:
            LOG.warning(f"Update called with no change: {self.file_path}")
            return
        if not self.write_changes():
            LOG.error("Disk contents are newer than this config object, changes were not written.")

    def remove_key(self, *key):
        for item in key:
            self.__sub__(item)

    def make_equal_by_keys(self, other: MutableMapping, recursive: bool = True, depth: int = 1):
        """
        Adds and removes keys from this config such that it has the same keys as 'other'. Configuration values are
        preserved with any added keys using default values from 'other'.
        Args:
            other: dict of keys and default values this configuration should have
            recursive: flag to indicate configuration may be merged recursively
            depth: int depth to recurse (0 includes top-level keys only)
        """
        with self.lock:
            old_content = deepcopy(self._content)
            if not recursive:
                depth = 0
            self._content = dict_make_equal_keys(self._content, other, depth)
            if old_content == self._content:
                return

        if not self.write_changes():
            # This is probably because multiple instances are syncing with default config simultaneously
            LOG.warning("Disk contents are newer than this config object, changes were not written.")
            self.check_reload()
            with self.lock:
                old_content = deepcopy(self._content)
                self._content = dict_make_equal_keys(self._content, other, depth)
            if old_content != self._content:
                LOG.error("Still found changes, writing them")
                success = self.write_changes()
                if not success:
                    LOG.error("Failed to write changes! Disk and config object are out of sync")

    def update_keys(self, other):
        """
        Adds keys to this config such that it has all keys in 'other'. Configuration values are
        preserved with any added keys using default values from 'other'.
        Args:
            other: dict of keys and default values this should be added to this configuration
        """
        with self.lock:
            old_content = deepcopy(self._content)
            self._content = dict_update_keys(self._content, other)  # to_change, one_with_all_keys
        if old_content == self._content:
            LOG.warning(f"Update called with no change: {self.file_path}")
            return

        if not self.write_changes():
            # This is probably because multiple instances are syncing with default config simultaneously
            LOG.warning("Disk contents are newer than this config object, changes were not written.")
            self.check_reload()
            with self.lock:
                old_content = deepcopy(self._content)
                self._content = dict_update_keys(old_content, other)
            if old_content != self._content:
                LOG.error("Still found changes, writing them")
                success = self.write_changes()
                if not success:
                    LOG.error("Failed to write changes! Disk and config object are out of sync")

    def check_for_updates(self) -> dict:
        """
        Reloads updated configuration from disk. Used to reload changes when other instances modify a configuration
        Returns:Updated configuration.content
        """
        with self.lock:
            new_content = self._load_yaml_file()
            if new_content:
                LOG.debug(f"{self.name} Checked for Updates")
                self._content = new_content
            elif self._content:
                LOG.error("new_content is empty! keeping current config")
        return self._content

    def update_yaml_file(self, header=None, sub_header=None, value="", multiple=False, final=False):
        """
        Called by class's children to update, create, or initiate a new parameter in the
        specified YAML file. Creates and updates headers, adds or overwrites preference elements,
        associates value to the created or existing field. Recursive if creating a new
        header-preference-value combo.
        :param multiple: true if more than one continuous write is coming
        :param header: string with the new or existing main header
        :param sub_header: new or existing subheader (sublist)
        :param value: any value that should be associated with the headers.
        :param final: true if this is the last change when skip_reload was true
        :return: pre-existing parameter if nothing to update or error if invalid yaml_type.
        """
        # with self.lock.acquire(30):
        self.check_reload()
        before_change = self._content

        LOG.debug(value)
        if header and sub_header:
            try:
                before_change[header][sub_header] = value
            except KeyError:
                before_change[header] = {sub_header: value}
                return
        elif header and not sub_header:
            try:
                before_change[header] = value
            except Exception as x:
                LOG.error(x)
        else:
            LOG.debug("No change needed")
            if not final:
                return

        if not multiple:
            if not self.write_changes():
                LOG.error("Disk contents are newer than this config object, changes were not written.")
        else:
            LOG.debug("More than one change")
            self._pending_write = True

    def export_to_json(self) -> str:
        """
        Export this configuration to a json file
        Returns: path to exported file
        """
        json_filename = os.path.join(self.path, f"{self.name}.json")
        write_to_json(self._content, json_filename)
        return json_filename

    def from_dict(self, pref_dict: dict):
        """
        Constructor to build this configuration object with the passed dict of data
        Args:
            pref_dict: dict to populate configuration with

        Returns: this object

        """
        self._content = pref_dict

        if not self.write_changes():
            LOG.error("Disk contents are newer than this config object, changes were not written.")
        return self

    def from_json(self, json_path: str):
        """
        Constructor to build this configuration object with the passed json file
        Args:
            json_path: Path to json file to populate configuration with

        Returns: this object

        """
        self._content = load_commented_json(json_path)

        if not self.write_changes():
            LOG.error("Disk contents are newer than this config object, changes were not written.")
        return self

    def _load_yaml_file(self) -> dict:
        """
        Loads and parses the YAML file at a given filepath into the Python
        dictionary object.
        :return: dictionary, containing all keys and values from the most current
                 selected YAML.
        """
        try:
            with open(self.file_path, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                except Exception as e:
                    LOG.error(e)
                    sleep(1)
                    f.seek(0)
                    try:
                        from ruamel.yaml import YAML
                        config = _make_loaded_config_safe(YAML().load(f))
                    except ImportError:
                        LOG.error(f"ruamel.yaml not available to load "
                                  f"legacy config. "
                                  f"pip install neon-utils[configuration]")
            if not config:
                LOG.debug(f"Empty config file found at: {self.file_path}")
                config = dict()
            self._loaded = os.path.getmtime(self.file_path)
            return config
        except FileNotFoundError:
            LOG.error(f"Configuration file not found! ({self.file_path})")
        except PermissionError:
            LOG.error(f"Permission Denied! ({self.file_path})")
        except Exception as c:
            LOG.error(f"{self.file_path} Configuration file error: {c}")
        return dict()

    def _write_yaml_file(self) -> bool:
        """
        Overwrites and/or updates the YML at the specified file_path.
        :return: True if changes were written to disk, else False
        """
        to_write = deepcopy(self._content)
        if not to_write:
            LOG.error(f"Config content empty! Skipping write to disk and reloading")
            return False
        if not path_is_read_writable(self.file_path):
            LOG.warning(f"Insufficient write permissions: {self.file_path}")
            return False
        with self.lock:
            if self._loaded != os.path.getmtime(self.file_path):
                LOG.warning("File on disk modified! Skipping write to disk")
                return False
            tmp_filename = join(self.path, f".{self.name}.tmp")
            # LOG.debug(f"tmp_filename={tmp_filename}")
            shutil.copy2(self.file_path, tmp_filename)
            try:
                with open(self.file_path, 'w+') as f:
                    yaml.safe_dump(to_write, f, allow_unicode=True,
                           default_flow_style=False, sort_keys=False)
                LOG.debug(f"YAML updated {self.name}")
                self._loaded = os.path.getmtime(self.file_path)
                self._pending_write = False
                self._disk_content_hash = hash(repr(self._content))
            except Exception as e:
                LOG.error(e)
                LOG.info(f"Restoring config from tmp file backup")
                shutil.copy2(tmp_filename, self.file_path)
            return True

    @property
    def content(self) -> dict:
        """
        Loads any changes from disk and returns an updated configuration dict
        Returns:
        dict content of this configuration object
        """
        self.check_reload()
        return self._content

    def get(self, *args) -> any:
        """
        Wraps content.get() to provide standard access to an updated configuration like a Python dictionary.
        Args:
            *args: args passed to self.content.get() (key and default value)

        Returns:
        self.content.get(*args)
        """
        return self.content.get(*args)

    def __getitem__(self, item):
        return self.content.get(item)

    def __contains__(self, item):
        return item in self._content

    def __setitem__(self, key, value):
        # LOG.info(f"Config changes pending write to disk!")
        self._pending_write = True
        self._content[key] = value

    def __repr__(self):
        return f"NGIConfig('{self.name}')@{self.file_path}"

    def __str__(self):
        return f"{self.file_path}: {json.dumps(self._content, indent=4)}"

    def __add__(self, other):
        # with self.lock.acquire(30):
        if other:
            if not isinstance(other, NGIConfig) and not isinstance(other, MutableMapping):
                raise AttributeError("__add__ expects dict or config object as argument")
            to_update = other
            if isinstance(other, NGIConfig):
                to_update = other._content
            if self._content:
                self._content.update(to_update)
            else:
                self._content = to_update
        else:
            raise TypeError("__add__ expects an argument other than None")
        if not self.write_changes():
            LOG.error("Disk contents are newer than this config object, changes were not written.")

    def __sub__(self, *other):
        # with self.lock.acquire(30):
        if other:
            for element in other:
                if isinstance(element, NGIConfig):
                    to_remove = list(element._content.keys())
                elif isinstance(element, MutableMapping):
                    to_remove = list(element.keys())
                elif isinstance(element, list):
                    to_remove = element
                elif isinstance(element, str):
                    to_remove = [element]
                else:
                    raise AttributeError("__add__ expects dict, list, str, or config object as the argument")

                if self._content:
                    self._content = delete_recursive_dictionary_keys(self._content, to_remove)
                else:
                    raise TypeError("{} config is empty".format(self.name))
        else:
            raise TypeError("__sub__ expects an argument other than None")
        if not self.write_changes():
            LOG.error("Disk contents are newer than this config object, changes were not written.")


def _get_legacy_config_dir(sys_path: Optional[list] = None) -> Optional[str]:
    """
    Get legacy configuration locations based on install directories
    :param sys_path: Optional list to override `sys.path`
    :return: path to save config to if one is found, else None
    """
    sys_path = sys_path or sys.path
    for p in [path for path in sys_path if sys_path]:
        if re.match(".*/lib/python.*/site-packages", p):
            # Get directory containing virtual environment
            clean_path = "/".join(p.split("/")[0:-4])
        else:
            clean_path = p
        invalid_path_prefixes = re.compile("^/usr|^/lib|.*/lib/python.*")
        valid_path_mapping = (
            (join(clean_path, "NGI"), join(clean_path, "NGI")),
            (join(clean_path, "neon_core"), clean_path),
            (join(clean_path, "mycroft"), clean_path),
            (join(clean_path, ".venv"), clean_path)
        )
        if re.match(invalid_path_prefixes, clean_path):
            # Exclude system paths
            continue
        for (path_to_check, path_to_write) in valid_path_mapping:
            if exists(path_to_check) and path_is_read_writable(path_to_write):
                return path_to_write
    return None


def _init_ovos_conf(name: str, force_reload: bool = False):
    """
    Perform a one-time init of ovos.conf for the calling module
    :param name: Name of calling module to configure to use `neon.yaml`
    :param force_reload: If true, force reload of configuration modules
    """
    from ovos_config.meta import get_ovos_config
    ovos_conf = get_ovos_config()
    original_conf = deepcopy(ovos_conf)
    ovos_conf.setdefault('module_overrides', {})
    ovos_conf.setdefault('submodule_mappings', {})

    if "neon_core" not in ovos_conf['module_overrides']:
        ovos_conf['module_overrides']['neon_core'] = {
            "base_folder": "neon",
            "config_filename": "neon.yaml"
        }

    if not ovos_conf.get('module_overrides',
                         {}).get("neon_core", {}).get("default_config_path"):
        from neon_utils.packaging_utils import get_neon_core_root
        try:
            default_config_dir = join(get_neon_core_root(), "configuration")
            if isfile(join(default_config_dir, "neon.yaml")):
                default_config_path = join(default_config_dir, "neon.yaml")
            elif isfile(join(default_config_dir, "neon.conf")):
                default_config_path = join(default_config_dir, "neon.conf")
            else:
                LOG.warning(f"No neon_core default config found in "
                            f"{default_config_dir}")
                default_config_path = None
            if default_config_path:
                ovos_conf["module_overrides"]["neon_core"][
                    "default_config_path"] = default_config_path
        except Exception as e:
            LOG.error(e)

    if name != "__main__" and name not in ovos_conf['submodule_mappings']:
        ovos_conf['submodule_mappings'][name] = 'neon_core'
        LOG.warning(f"Calling module ({name}) now configured to use neon.yaml")
        if name == "neon_core":
            ovos_conf['submodule_mappings']['neon_core.skills.skill_manager'] \
                = 'neon_core'

        ovos_path = join(xdg_config_home(), "OpenVoiceOS", "ovos.conf")
        os.makedirs(dirname(ovos_path), exist_ok=True)
        config_to_write = {
            "module_overrides": ovos_conf.get('module_overrides'),
            "submodule_mappings": ovos_conf.get('submodule_mappings')
        }
        with open(ovos_path, "w+") as f:
            json.dump(config_to_write, f, indent=4)

    if force_reload or ovos_conf != original_conf:
        LOG.debug("Force reload of all configuration references")
        # Note that the below block reloads modules in a specific order due to
        # imports within ovos_config and mycroft.configuration
        import ovos_config
        importlib.reload(ovos_config.locations)
        from ovos_config.meta import get_ovos_config
        ovos_conf = get_ovos_config()  # Load the full stack for /etc overrides
        if ovos_conf["module_overrides"]["neon_core"].get("default_config_path") \
            and ovos_config.locations.DEFAULT_CONFIG != \
                ovos_conf["module_overrides"]["neon_core"]["default_config_path"]:
            ovos_config.locations.DEFAULT_CONFIG = \
                ovos_conf["module_overrides"]["neon_core"]["default_config_path"]

            # Default config changed, remove any cached configuration
            del ovos_config.config.Configuration
            del ovos_config.Configuration

        import ovos_config.models
        importlib.reload(ovos_config.models)
        importlib.reload(ovos_config.config)
        importlib.reload(ovos_config)

        try:
            import mycroft.configuration
            import mycroft.configuration.locations
            import mycroft.configuration.config
            del mycroft.configuration.Configuration
            importlib.reload(mycroft.configuration.locations)
            importlib.reload(mycroft.configuration.config)
            importlib.reload(mycroft.configuration)
        except Exception as e:
            LOG.error(f"Failed to override mycroft.configuration: {e}")


def _validate_config_env() -> bool:
    """
    Check that XDG_CONFIG_HOME and NEON_CONFIG_PATH match for compatibility. If
    config path isn't writable, relocate files to a valid directory and update
    envvars.
    :return: True if configuration files were moved
    """
    neon_spec = os.getenv("NEON_CONFIG_PATH")
    xdg_spec = os.getenv("XDG_CONFIG_HOME")

    if neon_spec and xdg_spec:
        LOG.warning("Configuration over-defined. Using XDG spec")
        LOG.info(f"xdg={xdg_spec}|neon={neon_spec}")
        os.environ["NEON_CONFIG_PATH"] = join(xdg_spec, "neon")
    elif xdg_spec:
        LOG.debug("Setting NEON_CONFIG_PATH for backwards-compat")
        os.environ["NEON_CONFIG_PATH"] = join(xdg_spec, "neon")
        return False
    elif neon_spec:
        # Path to Neon config spec'd (probably Docker)
        LOG.info(f"NEON_CONFIG_PATH={neon_spec}")
        if neon_spec.endswith("/neon") and path_is_read_writable(neon_spec):
            # We can handle this path as XDG
            xdg = dirname(neon_spec)
            LOG.warning(f"NEON_CONFIG_PATH set, "
                        f"updating XDG_CONFIG_HOME to {xdg}")
            os.environ["XDG_CONFIG_HOME"] = xdg
            return False
    else:
        # No path configured, just set Neon spec to default XDG
        LOG.info("Setting NEON_CONFIG_PATH to xdg default ~/.config/neon")
        os.environ["NEON_CONFIG_PATH"] = expanduser("~/.config/neon")
        return False

    # Paths like '/config' can't be translated to XDG, just move files
    from glob import glob
    real_config_path = get_config_dir()
    moved = False
    if neon_spec != real_config_path:
        LOG.warning("NEON_CONFIG_PATH is not XDG-compatible. "
                    "copying config")
        for file in glob(f'{neon_spec}/*'):
            if any((file.endswith(x) for x in ('.yml', '.yaml',
                                               '.json', '.conf'))):
                shutil.copy2(file, join(real_config_path, basename(file)))
                LOG.info(f"Copied {file} to {real_config_path}")
                moved = True
            else:
                LOG.debug(f"Ignoring non-config {file}")
    os.environ["NEON_CONFIG_PATH"] = real_config_path
    return moved


def _check_legacy_config() -> str:
    """
    Return the path to valid legacy core configuration
    """
    os.environ["NEON_CONFIG_PATH"] = os.getenv("NEON_CONFIG_PATH") or \
        get_config_dir()
    return join(os.getenv("NEON_CONFIG_PATH"), "ngi_local_conf.yml")


def init_config_dir():
    """
    Performs one-time initialization of the configuration directory.
    NOTE: This method is intended to be called once at module init, before any
    configuration is loaded. Repeated calls or calls after configuration is
    loaded may lead to inconsistent behavior.
    """

    old_config_file = _check_legacy_config()

    # Ensure envvars are consistent and valid (read/writeable)
    force_reload = _validate_config_env()
    if isfile(old_config_file):
        new_config_path = get_config_dir()
        if isfile(join(new_config_path, "neon.yaml")):
            LOG.error("Config already exists, skipping migration")
        else:
            LOG.warning(f"Migrating legacy config: {old_config_file}")
            migrate_ngi_config(old_config_file,
                               join(new_config_path, "neon.yaml"))
            LOG.info(f"Wrote new config: {join(new_config_path, 'neon.yaml')}")
        if path_is_read_writable(dirname(old_config_file)):
            shutil.move(old_config_file,
                        splitext(old_config_file)[0] + ".bak")
            LOG.info(f"Archived {old_config_file}")
        valid_legacy_config = join(new_config_path, "ngi_local_conf.yml")
        if isfile(valid_legacy_config):
            shutil.move(valid_legacy_config,
                        splitext(valid_legacy_config)[0] + ".bak")
            LOG.info(f"Archived {valid_legacy_config}")
    import inspect

    stack = inspect.stack()
    mod = inspect.getmodule(stack[1][0])
    name = mod.__name__.split('.')[0] if mod else ''

    # Ensure `ovos.conf` specifies this module as using `neon.yaml`
    _init_ovos_conf(name, force_reload)


def get_config_dir():
    """
    Get a default directory in which to find Neon configuration files,
    creating it if it doesn't exist.
    Returns: Path to configuration or else default
    """
    config_path = join(xdg_config_home(), "neon")
    LOG.debug(config_path)
    if not isdir(config_path):
        LOG.info(f"Creating config directory: {config_path}")
        os.makedirs(config_path)
    return config_path


def delete_recursive_dictionary_keys(dct_to_change: MutableMapping,
                                     list_of_keys_to_remove: list) -> \
        MutableMapping:
    """
    Removes the specified keys from the specified dict.
    Args:
        dct_to_change: Dictionary to modify
        list_of_keys_to_remove: List of keys to remove

    Returns: dct_to_change with any specified keys removed

    """
    if not isinstance(dct_to_change, MutableMapping) or not \
            isinstance(list_of_keys_to_remove, list):
        raise AttributeError("delete_recursive_dictionary_keys expects "
                             "a dict and a list as args")

    for key in list_of_keys_to_remove:
        with suppress(KeyError):
            del dct_to_change[key]
    for value in list(dct_to_change.values()):
        if isinstance(value, MutableMapping):
            delete_recursive_dictionary_keys(value, list_of_keys_to_remove)
    return dct_to_change


def dict_merge(dct_to_change: MutableMapping,
               merge_dct: MutableMapping) -> MutableMapping:
    """
    Recursively merges two configuration dictionaries and returns the
    combined object. All keys are returned with values from merge_dct
    overwriting those from dct_to_change.
    Args:
        dct_to_change: dict to append keys and values to
        merge_dct: dict with keys and new values to add to dct_to_change
    Returns: dict of merged preferences
    """
    if not isinstance(dct_to_change, MutableMapping) or not \
            isinstance(merge_dct, MutableMapping):
        raise AttributeError("merge_recursive_dicts expects "
                             "two dict objects as args")
    for key, value in merge_dct.items():
        if isinstance(dct_to_change.get(key), dict) and \
                isinstance(value, MutableMapping):
            dct_to_change[key] = dict_merge(dct_to_change[key], value)
        else:
            dct_to_change[key] = value
    return dct_to_change


def dict_make_equal_keys(dct_to_change: MutableMapping,
                         keys_dct: MutableMapping,
                         max_depth: int = 1,
                         cur_depth: int = 0) -> MutableMapping:
    """
    Adds and removes keys from dct_to_change such that it has the same keys
    as keys_dct. Values from dct_to_change are preserved with any added keys
    using default values from keys_dct.
    Args:
        dct_to_change: Dict of user preferences to modify and return
        keys_dct: Dict containing all keys and default values
        max_depth: Int depth to recurse (0-indexed)
        cur_depth: Current depth relative to top-level config (0-indexed)
    Returns: dct_to_change with any keys not in keys_dct removed and any new
        keys added with default values

    """
    if not isinstance(dct_to_change, MutableMapping) or not \
            isinstance(keys_dct, MutableMapping):
        raise AttributeError("merge_recursive_dicts expects two dict objects "
                             "as args")
    if not keys_dct:
        raise ValueError("Empty keys_dct provided, not modifying anything.")
    for key in list(dct_to_change.keys()):
        if isinstance(keys_dct.get(key), dict) and \
                isinstance(dct_to_change[key], MutableMapping):
            if max_depth > cur_depth:
                if key in ("tts", "stt", "hotwords", "language"):
                    dct_to_change[key] = dict_update_keys(dct_to_change[key],
                                                          keys_dct[key])
                else:
                    try:
                        dct_to_change[key] = \
                            dict_make_equal_keys(dct_to_change[key], keys_dct[key],
                                                 max_depth, cur_depth + 1)
                    except ValueError:
                        pass
        elif key not in keys_dct.keys():
            dct_to_change.pop(key)
            LOG.warning(f"Removing '{key}' from dict!")
            # del dct_to_change[key]
    for key, value in keys_dct.items():
        if key not in dct_to_change.keys():
            dct_to_change[key] = value
    return dct_to_change


def dict_update_keys(dct_to_change: MutableMapping,
                     keys_dct: MutableMapping) -> MutableMapping:
    """
    Adds keys to dct_to_change such that all keys in keys_dict exist in
    dict_to_change. Added keys use default values from keys_dict
    Args:
        dct_to_change: Dict of user preferences to modify and return
        keys_dct: Dict containing potentially new keys and default values

    Returns: dct_to_change with any new keys in keys_dict added with defaultS

    """
    if not isinstance(dct_to_change, MutableMapping) or not \
            isinstance(keys_dct, MutableMapping):
        raise AttributeError("merge_recursive_dicts expects two dict "
                             "objects as args")
    for key, value in list(keys_dct.items()):
        if isinstance(keys_dct.get(key), dict) and isinstance(value,
                                                              MutableMapping):
            dct_to_change[key] = dict_update_keys(dct_to_change.get(key, {}),
                                                  keys_dct[key])
        else:
            if key not in dct_to_change.keys():
                dct_to_change[key] = value
    return dct_to_change


def write_to_json(preference_dict: MutableMapping, output_path: str):
    """
    Writes the specified dictionary to a json file
    Args:
        preference_dict: Dict to write to JSON
        output_path: Output file to write
    """
    if not os.path.exists(output_path):
        create_file(output_path)
    with open(output_path, "w") as out:
        json.dump(preference_dict, out, indent=4)


def get_user_config_from_mycroft_conf(user_config: dict = None) -> dict:
    """
    Populates user_config with values from mycroft.conf
    :returns: dict modified or created user config
    """
    from ovos_config.models import MycroftUserConfig
    user_config = user_config or \
        deepcopy(NGIConfig("default_user_conf",
                           os.path.join(os.path.dirname(__file__),
                                        "default_configurations")).content)
    mycroft_config = MycroftUserConfig()
    user_config["speech"]["stt_language"] = mycroft_config.get("lang", "en-us")
    user_config["speech"]["tts_language"] = mycroft_config.get("lang", "en-us")
    user_config["speech"]["alt_languages"] = \
        mycroft_config.get("secondary_langs", [])
    user_config["units"]["time"] = \
        12 if mycroft_config.get("time_format", "half") == "half" else 24
    user_config["units"]["date"] = mycroft_config.get("date_format") or "MDY"
    user_config["units"]["measure"] = \
        "metric" if mycroft_config.get("system_unit") == "metric" \
        else "imperial"

    if mycroft_config.get("location"):
        user_config["location"] = {
            "lat": str(mycroft_config["location"]["coordinate"]["latitude"]),
            "lng": str(mycroft_config["location"]["coordinate"]["longitude"]),
            "city": mycroft_config["location"]["city"]["name"],
            "state": mycroft_config["location"]["city"]["state"]["name"],
            "country": mycroft_config["location"]["city"]["state"]
            ["country"]["name"],
            "tz": mycroft_config["location"]["timezone"]["code"],
            "utc": str(round(mycroft_config["location"]["timezone"]["offset"]
                             / 3600000, 1))}
    return user_config


def get_neon_user_config(path: Optional[str] = None) -> NGIConfig:
    """
    Returns a dict user configuration and handles any migration of
    configuration values to local config from user config
    Args:
        path: optional path to yml configuration files
    Returns:
        NGIConfig object with user config
    """
    try:
        user_config = NGIConfig("ngi_user_info", path)
    except PermissionError:
        LOG.error(f"Insufficient Permissions for path: {path}")
        user_config = NGIConfig("ngi_user_info")
    _populate_read_only_config(path, basename(user_config.file_path),
                               user_config)
    default_user_config = NGIConfig("default_user_conf",
                                    os.path.join(os.path.dirname(__file__),
                                                 "default_configurations"))
    if len(user_config.content) == 0:
        LOG.info("Created Empty User Config!")
        user_config.populate(default_user_config.content)
        get_user_config_from_mycroft_conf(user_config.content)
        LOG.debug("Updated user config from mycroft.conf")
        user_config.write_changes()

    user_config.make_equal_by_keys(default_user_config.content)
    return user_config


def is_neon_core() -> bool:
    """
    Checks for neon-specific packages to determine if
    this is a Neon Core or a Mycroft Core
    Returns:
        True if core is Neon, else False
    """
    import importlib.util
    if importlib.util.find_spec("neon_core"):
        return True
    if importlib.util.find_spec("neon_core_client"):
        LOG.info("Found neon_core_client; assuming neon_core")
        return True
    if importlib.util.find_spec("neon_core_server"):
        LOG.info("Found neon_core_server; assuming neon_core")
        return True
    return False


def get_mycroft_compatible_location(location: dict) -> dict:
    """
    Translates a user config location to a Mycroft-compatible config dict
    :param location: dict location parsed from user config
    :returns: dict formatted to match mycroft.conf spec
    """
    from neon_utils.parse_utils import clean_quotes
    if not any((location['lat'], location['lng'],
                location['city'], location['tz'])):
        LOG.debug('Neon config empty, return core value')
        return _safe_mycroft_config().get('location')
    try:
        lat = clean_quotes(location['lat'])
        lng = clean_quotes(location['lng'])
    except (TypeError, ValueError):
        lat = location['lat']
        lng = location['lng']
    # TODO: Define state/country codes in location config DM
    # try:
    #     parsed_location = get_full_location((lat, lng))
    # except Exception as e:
    #     LOG.exception(e)
    #     parsed_location = None
    if location.get("country") and \
            location.get("country").lower() == "united states":
        location["country_code"] = "us"

    if location.get('utc'):
        try:
            offset = float(clean_quotes(location["utc"]))
        except TypeError:
            offset = float(location["utc"])
        except ValueError:
            offset = 0.0
    else:
        offset = 0.0

    try:
        lat = float(lat)
        lng = float(lng)
    except Exception as e:
        LOG.exception(e)

    location = {
        "city": {
            "code": location["city"],
            "name": location["city"],
            "state": {
                "code": location.get("state_code") or "",
                "name": location["state"],
                "country": {
                    "code": location.get("country_code") or "",
                    "name": location["country"]
                }
            }
        },
        "coordinate": {
            "latitude": lat,
            "longitude": lng
        },
        "timezone": {
            "code": location["tz"],
            "name": location["tz"],  # TODO: Util to parse this
            "offset": offset * 3600000,
            "dstOffset": 3600000
        }
    }
    return location


def get_mycroft_compatible_config(mycroft_only=False,
                                  neon_config_path=None) -> dict:
    """
    Get a configuration compatible with mycroft.conf/ovos.conf
    NOTE: This method should only be called at startup to write a .conf file
    :param mycroft_only: if True, ignore Neon configuration files
    :param neon_config_path: optional path override to yml config directory
    :returns: dict config compatible with mycroft.conf structure
    """
    default_config = _safe_mycroft_config()
    if mycroft_only:
        return default_config
    speech = _get_neon_speech_config(neon_config_path)
    user = get_neon_user_config(neon_config_path) if \
        isfile(join(neon_config_path or get_config_dir(),
                    "ngi_user_info.yml")) else \
        NGIConfig("default_user_conf", os.path.join(os.path.dirname(__file__),
                                                    "default_configurations"))
    local = _get_neon_local_config(neon_config_path)

    default_config["lang"] = "en-us"
    default_config["system_unit"] = user["units"]["measure"]
    default_config["time_format"] = \
        "half" if user["units"]["time"] == 12 else "full"
    default_config["date_format"] = user["units"]["date"]
    default_config["opt_in"] = local.get("prefFlags", {}).get("metrics", False)
    default_config["confirm_listening"] = \
        local.get("interface", {}).get("confirm_listening", True)
    default_config["sounds"] = {**default_config.get("sounds", {}),
                                **local.get("sounds", {})}

    default_config["location"] = \
        get_mycroft_compatible_location(user.get("location"))

    default_config["data_dir"] = local.get("dirVars", {}).get("rootDir")
    default_config["cache_path"] = local.get("dirVars", {}).get("cacheDir")
    default_config["skills"] = _get_neon_skills_config(neon_config_path)
    default_config["server"] = _get_neon_api_config(neon_config_path)
    default_config["websocket"] = _get_neon_bus_config(neon_config_path)
    default_config["gui_websocket"] = {**default_config.get("gui_websocket",
                                                            {}),
                                       **local.get("gui", {})}
    default_config["gui_websocket"]["base_port"] = \
        default_config["gui_websocket"].get("base_port") or \
        default_config["gui_websocket"].get("port")

    default_config["listener"] = speech["listener"]
    default_config["hotwords"] = speech["hotwords"]
    default_config["log_level"] = local.get("logs", {}).get("log_level") or \
        default_config.get("log_level")
    default_config["session"] = local.get("session") or \
        default_config.get("session")
    default_config["stt"] = speech["stt"]
    default_config["tts"] = local.get("tts") or default_config.get("tts") or {}
    default_config["padatious"] = {**default_config.get("padatious", {}),
                                   **local.get("padatious", {})}
    default_config["Audio"] = _get_neon_audio_config(neon_config_path)["Audio"]
    default_config["debug"] = local.get("prefFlags", {}.get("devMode", False))

    default_config["language"] = _get_neon_lang_config(neon_config_path)
    default_config["keys"] = _get_neon_auth_config(neon_config_path)
    default_config["text_parsers"] = {**default_config.get("text_parsers",
                                                           {}),
                                      **local.get("text_parsers", {})}
    default_config["audio_parsers"] = speech["audio_parsers"]
    default_config["disable_xdg"] = False
    default_config["ipc_path"] = local.get("dirVars", {}).get("ipcDir") or \
        default_config.get("ipc_path")
    default_config["remote-server"] = local.get("gui", {}).get("file_server")
    default_config["ready_settings"] = local.get("ready_settings") or \
        default_config.get("ready_settings")
    default_config["device_name"] = local.get("devVars", {}).get("devName") or\
        default_config.get("device_name")
    default_config["MQ"] = local.get("MQ", {})

    if local.get("dirVars", {}).get("logsDir"):
        default_config["log_dir"] = local["dirVars"]["logsDir"]

    return default_config


def write_mycroft_compatible_config(file_to_write: str = None) -> str:
    """
    Generates a mycroft-like configuration and writes it to the specified file
    NOTE: This is potentially destructive and will overwrite existing config
    :param file_to_write: config file to write out
    :return: path to written config file
    """
    file_to_write = file_to_write or "~/.mycroft/mycroft.conf"
    configuration = get_mycroft_compatible_config()
    file_path = os.path.expanduser(file_to_write)

    if isfile(file_path):
        disk_config = load_commented_json(file_path)
        if disk_config == configuration:
            LOG.debug(f"Configuration already up to date")
            return file_path
        LOG.warning(f"File exists and will be overwritten: {file_to_write}")
    elif not isdir(dirname(file_path)):
        os.makedirs(dirname(file_path))

    with NamedLock(file_path):
        with open(file_path, 'w') as f:
            json.dump(configuration, f, indent=4)
    return file_path


def create_config_from_setup_params(path=None) -> dict:
    """
    Populate a (probably) new local config with setup parameters
    Args:
        path: Optional config path
    Returns:
        NGIConfig object generated from environment vars
    """

    dev_mode = (os.environ.get("devMode") or "false") == "true"
    # auto_run = os.environ.get("autoStart") or "false" == "true"
    auto_update = (os.environ.get("autoUpdate") or "false") == "true"
    neon_token = os.environ.get("GITHUB_TOKEN")
    tts_module = os.environ.get("ttsModule")
    stt_module = os.environ.get("sttModule")
    translation_module = os.environ.get("translateModule")
    detection_module = os.environ.get("detectionModule")
    device_name = os.environ.get("devName") or "unknown"
    logs_dir = os.environ.get("logsDir")
    if os.environ.get("skillRepo"):
        default_skills = os.environ["skillRepo"]
    elif dev_mode:
        default_skills = "https://raw.githubusercontent.com/NeonGeckoCom/" \
                         "neon_skills/master/skill_lists/DEFAULT-SKILLS-DEV"
    else:
        default_skills = "https://raw.githubusercontent.com/NeonGeckoCom/" \
                         "neon_skills/master/skill_lists/DEFAULT-SKILLS"

    config_patch = {
        "debug": dev_mode,
        "skills": {
            "auto_update": auto_update,
            "neon_token": neon_token,
            "default_skills": default_skills
        },
        "tts": {},
        "stt": {},
        "language": {},
        "device_name": device_name,
        "log_dir": logs_dir
    }
    if tts_module:
        config_patch["tts"]["module"] = tts_module
    if stt_module:
        config_patch["stt"]["module"] = stt_module
    if translation_module:
        config_patch["language"]["translation_module"] = translation_module
    if detection_module:
        config_patch["language"]["detection_module"] = detection_module

    output_path = join((path or join(xdg_config_home(), "neon")), "neon.yaml")
    if not isdir(dirname(output_path)):
        os.makedirs(dirname(output_path))
    with open(output_path, "w+") as f:
        yaml.safe_dump(config_patch, f)
    LOG.info(f"Dumped new config to: {output_path}")
    return config_patch


def migrate_ngi_config(old_config_path: str = None,
                       new_config_path: str = None):
    """
    Migrate an old ngi_local_conf.yml to mycroft-style config
    :param old_config_path: path to ngi_local_conf.yml file to read
    :param new_config_path: path to output yaml file to write
    """
    old_config_path = expanduser(old_config_path or _get_legacy_config_dir())
    if not isfile(old_config_path):
        old_config_path = join(old_config_path, "ngi_local_conf.yml")
    if not isfile(old_config_path):
        raise FileNotFoundError(f"No config at path: {old_config_path}")

    new_config_path = new_config_path or join(xdg_config_home(),
                                              "neon", "neon.yaml")
    compat_config = get_mycroft_compatible_config(
        neon_config_path=dirname(old_config_path))
    try:
        with open(new_config_path, 'w+') as f:
            yaml.safe_dump(compat_config, f, allow_unicode=True,
                           default_flow_style=False, sort_keys=False)
    except Exception as e:
        LOG.exception(e)
        LOG.error(compat_config)
    LOG.warning(f"Migrated old config to: {new_config_path}")


def parse_skill_default_settings(settings_meta: dict) -> dict:
    """
    Parses default skill settings from settingsmeta file contents
    :param settings_meta: parsed contents of settingsmeta.yml or
    settingsmeta.json
    :return: parsed dict of default settings keys/values
    """
    if not isinstance(settings_meta, dict):
        LOG.error(settings_meta)
        raise TypeError(f"Expected a dict, got: {type(settings_meta)}")
    if not settings_meta:
        LOG.debug(f"Empty Settings")
        return dict()
    else:
        settings = dict()
        try:
            for settings_group in settings_meta.get("skillMetadata",
                                                    dict()).get("sections",
                                                                list()):
                for field in settings_group.get("fields", list()):
                    settings = {**settings,
                                **{field.get("name"): field.get("value")}}
            return settings
        except Exception as e:
            LOG.error(e)
            raise e


def _make_loaded_config_safe(config: dict) -> dict:
    """
    Ensure the entire passed config object is json-serializable
    :param config: "dirty" config object with OrderedDict, etc. items
    :returns: dict containing only primitive objects
        (list, dict, str, float, etc.)
    """
    return json.loads(json.dumps(config))


# TODO: Below methods are all deprecated and retained only for backwards-compat
def get_neon_auth_config(*args, **kwargs):
    LOG.error("This method is deprecated")
    return {"api_services": {}}


def _get_neon_lang_config(neon_config_path=None) -> dict:
    """
    Get a language config for language utilities
    Returns:
        dict of config params used by Language Detector and Translator modules
    """
    import inspect
    call = inspect.stack()[1]
    module = inspect.getmodule(call.frame)
    name = module.__name__ if module else call.filename
    LOG.warning("This reference is deprecated - "
                f"{name}:{call.lineno}")
    lang_config = deepcopy(_get_neon_local_config(neon_config_path).content.get("language", {}))
    lang_config["internal"] = lang_config.pop("core_lang", "en-us")
    lang_config["boost"] = lang_config.get("boost", False)
    merged_language = {**_safe_mycroft_config().get("language", {}), **lang_config}
    if merged_language.keys() != lang_config.keys():
        LOG.warning(f"Keys missing from Neon config! {merged_language.keys()}")

    return merged_language


def _get_neon_tts_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for TTS
    Returns:
    dict of TTS-related configuration
    """
    return _get_neon_local_config(neon_config_path).get("tts") or {}


def _get_neon_speech_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for listener. Merge any values from Mycroft config if missing from Neon.
    Returns:
        dict of config params used for listener in neon_speech
    """
    mycroft = _safe_mycroft_config()
    local_config = _get_neon_local_config(neon_config_path)
    # for section in local_config.content:
    #     if isinstance(local_config[section], dict):
    #         for subsection in local_config[section]:
    #             if isinstance(local_config[section][subsection], dict):
    #                 local_config[section][subsection] = dict(local_config[section][subsection])
    #         local_config[section] = dict(local_config[section])
    neon_listener_config = deepcopy(local_config.get("listener", {}))
    neon_listener_config["wake_word_enabled"] = local_config.get("interface", {}).get("wake_word_enabled", True)
    neon_listener_config["save_utterances"] = local_config.get("prefFlags", {}).get("saveAudio", False)
    neon_listener_config["confirm_listening"] = local_config.get("interface", {}).get("confirm_listening", True)
    neon_listener_config["record_utterances"] = neon_listener_config["save_utterances"]
    neon_listener_config["record_wake_words"] = neon_listener_config["save_utterances"]
    merged_listener = {**mycroft.get("listener", {}), **neon_listener_config}
    if merged_listener.keys() != neon_listener_config.keys():
        LOG.warning(f"Keys missing from Neon config! {merged_listener.keys()}")

    lang = mycroft.get("language", {}).get("internal", "en-us")  # core_lang

    neon_stt_config = local_config.get("stt", {})
    merged_stt_config = {**mycroft.get("stt", {}), **neon_stt_config}
    # stt keys will vary by installed/configured plugins
    # if merged_stt_config.keys() != neon_stt_config.keys():
    #     LOG.warning(f"Keys missing from Neon config! {merged_stt_config.keys()}")

    hotword_config = local_config.get("hotwords") or mycroft.get("hotwords")
    if hotword_config != local_config.get("hotwords"):
        LOG.warning(f"Neon hotword config missing! {hotword_config}")

    neon_audio_parser_config = local_config.get("audio_parsers", {})
    merged_audio_parser_config = {**mycroft.get("audio_parsers", {}), **neon_audio_parser_config}
    if merged_audio_parser_config.keys() != neon_audio_parser_config.keys():
        LOG.warning(f"Keys missing from Neon config! {merged_audio_parser_config.keys()}")

    return {"listener": merged_listener,
            "hotwords": hotword_config,
            "audio_parsers": merged_audio_parser_config,
            "lang": lang,
            "stt": merged_stt_config,
            "metric_upload": local_config.get("prefFlags", {}).get("metrics", False),
            "remote_server": local_config.get("remoteVars", {}).get("remoteHost", "64.34.186.120"),
            "data_dir": os.path.expanduser(local_config.get("dirVars", {}).get("rootDir") or "~/.local/share/neon"),
            "keys": {}
            }


def _get_neon_bus_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for the messagebus. Merge any values from Mycroft config if missing from Neon.
    Returns:
        dict of config params used for a messagebus client
    """
    mycroft = _safe_mycroft_config().get("websocket", {})
    neon = _get_neon_local_config(neon_config_path).get("websocket", {})
    merged = {**mycroft, **neon}
    if merged.keys() != neon.keys():
        LOG.warning(f"Keys missing from Neon config! {merged.keys()}")
    return merged


def _get_neon_audio_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for the audio module.
    Merge any values from Mycroft config if missing from Neon.
    Returns:
        dict of config params used for the Audio module
    """
    mycroft = _safe_mycroft_config()
    local_config = _get_neon_local_config(neon_config_path)
    neon_audio = local_config.get("audioService", {})
    for section in neon_audio:
        if isinstance(neon_audio[section], dict):
            for s in neon_audio[section]:
                if isinstance(neon_audio[section][s], dict):
                    neon_audio[section][s] = dict(neon_audio[section][s])
            neon_audio[section] = dict(neon_audio[section])
    merged_audio = {**mycroft.get("Audio", {}), **neon_audio}
    # tts keys will vary by installed/configured plugins
    # if merged_audio.keys() != neon_audio.keys():
    #     LOG.warning(f"Keys missing from Neon config! {merged_audio.keys()}")

    return {"Audio": merged_audio,
            "tts": _get_neon_tts_config(),
            "language": _get_neon_lang_config()}


def _get_neon_api_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for the api module.
    Merge any values from Mycroft config if missing from Neon.
    Returns:
        dict of config params used for the Mycroft API module
    """
    core_config = _get_neon_local_config(neon_config_path)
    api_config = deepcopy(core_config.get("api", {}))
    api_config["metrics"] = core_config.get("prefFlags", {}).get("metrics", False)
    mycroft = _safe_mycroft_config().get("server", {})
    merged = {**mycroft, **api_config}
    if merged.keys() != api_config.keys():
        LOG.warning(f"Keys missing from Neon config! {merged.keys()}")
    return merged


def _get_neon_skills_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for the skills module.
    Merge any values from Mycroft config if missing from Neon.
    Returns:
        dict of config params used for the Mycroft Skills module
    """
    core_config = _get_neon_local_config(neon_config_path)
    mycroft_config = _safe_mycroft_config()
    neon_skills = deepcopy(core_config.get("skills", {}))
    # neon_skills["directory"] = \
    #     os.path.expanduser(core_config["dirVars"].get("skillsDir"))
    # mycroft_config['skills'].setdefault("extra_directories", [])
    # mycroft_config['skills']['extra_directories'].\
    #     insert(0, os.path.expanduser(core_config["dirVars"].get("skillsDir")))
    # Patch msm config for skills backwards-compat.
    neon_skills["msm"] = {"directory": neon_skills.get("directory"),
                          "versioned": False,
                          "repo": {"branch": "",
                                   "cache": "",
                                   "url": ""}}

    try:
        ovos_core_version = get_package_version_spec("ovos-core")
        if ovos_core_version.startswith("0.0.1"):
            # ovos-core 0.0.1 uses directory_override param
            LOG.debug("Adding `directory_override` setting for ovos-core")
            neon_skills["directory_override"] = neon_skills["directory"]
    except ModuleNotFoundError:
        LOG.warning("ovos-core not installed")
        neon_skills["directory_override"] = neon_skills["directory"]

    neon_skills["disable_osm"] = neon_skills.get("skill_manager", "osm") != "osm"
    neon_skills["priority_skills"] = neon_skills.get("priority") or []
    neon_skills["blacklisted_skills"] = neon_skills.get("blacklist") or []

    if not isinstance(neon_skills.get("auto_update_interval"), float):
        try:
            neon_skills["auto_update_interval"] = \
                float(neon_skills.get("auto_update_interval") or 24.0)
        except Exception as e:
            LOG.error(e)
            neon_skills["auto_update_interval"] = 24.0
    if not isinstance(neon_skills.get("appstore_sync_interval"), float):
        try:
            neon_skills["appstore_sync_interval"] = \
                float(neon_skills.get("appstore_sync_interval") or 6.0)
        except Exception as e:
            LOG.error(e)
            neon_skills["appstore_sync_interval"] = 6.0
    neon_skills["update_interval"] = neon_skills["auto_update_interval"]  # Backwards Compat.
    if not neon_skills.get("neon_token"):
        try:
            neon_skills["neon_token"] = find_neon_git_token()
            # populate_github_token_config(neon_skills["neon_token"])
        except FileNotFoundError:
            LOG.debug(f"No Github token found; skills may fail to install")
            neon_skills["neon_token"] = None
    skills_config = {**mycroft_config.get("skills", {}), **neon_skills}
    skills_config.setdefault("debug", False)
    return skills_config


def _get_neon_transcribe_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for the transcription module.
    Returns:
        dict of config params used for the Neon transcription module
    """
    local_config = _get_neon_local_config(neon_config_path)
    user_config = get_neon_user_config(neon_config_path) if \
        isfile(join(neon_config_path or get_config_dir(),
                    "ngi_user_info.yml")) else {}
    neon_transcribe_config = dict()
    neon_transcribe_config["transcript_dir"] = \
        local_config.get("dirVars", {}).get("docsDir", "")
    neon_transcribe_config["audio_permission"] = \
        user_config.get("privacy", {}).get("save_audio", False)
    return neon_transcribe_config


def _get_neon_gui_config(neon_config_path=None) -> dict:
    """
    Get a configuration dict for the gui module.
    Returns:
        dict of config params used for the Neon gui module
    """
    local_config = _get_neon_local_config(neon_config_path)
    gui_config = dict(local_config.get("gui", {}))
    gui_config["base_port"] = gui_config.get("port")
    return gui_config


def _safe_mycroft_config() -> dict:
    """
    Safe reference to mycroft config that always returns a dict
    Returns:
        dict mycroft configuration
    """
    from ovos_config.config import Configuration
    config = Configuration()
    return dict(config)


def _get_neon_yaml_config() -> dict:
    from ovos_config.meta import get_ovos_config
    from ovos_config.locations import get_xdg_config_save_path
    from ovos_utils.json_helper import merge_dict

    with open(get_ovos_config()["default_config_path"]) as f:
        default = yaml.safe_load(f)
    config = dict(default)
    system_config = os.environ.get("MYCROFT_SYSTEM_CONFIG",
                                   "/etc/neon/neon.yaml")
    user_config = join(get_xdg_config_save_path("neon"), "neon.yaml")
    if isfile(system_config):
        with open(system_config) as f:
            system = yaml.safe_load(f)
        config = merge_dict(config, system)

    if isfile(user_config):
        with open(user_config) as f:
            user = yaml.safe_load(f)
        config = merge_dict(config, user)

    return config


def _get_neon_auth_config(path: Optional[str] = None) -> dict:
    """
    Returns a dict authentication configuration and handles populating values
    from key files
    Args:
        path: optional path to yml configuration files
    Returns:
        NGIConfig object with authentication config
    """
    if isfile(join(path or get_config_dir(), "ngi_auth_vars.yml")):
        try:
            auth_config = NGIConfig("ngi_auth_vars", path)
        except PermissionError:
            LOG.error(f"Insufficient Permissions for path: {path}")
            auth_config = NGIConfig("ngi_auth_vars")
            _populate_read_only_config(path, basename(auth_config.file_path),
                                       auth_config)
        if not auth_config.content:
            LOG.info("Populating empty auth configuration")
            auth_config._content = build_new_auth_config(path)
            auth_config['api_services'] = {
                'wolfram_alpha': auth_config.get('wolfram_alpha') or {},
                'alpha_vantage': auth_config.get('alpha_vantage') or {},
                'open_weather_map': auth_config.get('open_weather_map') or {}
            }
            auth_config.write_changes()

        if not auth_config.content:
            LOG.info("Empty auth_config generated, adding 'created' key to "
                     "prevent regeneration attempts")
            auth_config._content = {"_loaded": True}
            auth_config.write_changes()
        # LOG.info(f"Loaded auth config from {auth_config.file_path}")
        # for key in auth_config.content:
        #     if isinstance(auth_config[key], dict):
        #         for sub in auth_config[key]:
        #             if isinstance(auth_config[key][sub], dict):
        #                 auth_config[key][sub] = dict(auth_config[key][sub])
        #         auth_config[key] = dict(auth_config[key])
        return dict(auth_config.content)
    else:
        auth_config = build_new_auth_config(path)
        auth_config['api_services'] = {
            'wolfram_alpha': auth_config.get('wolfram_alpha') or {},
            'alpha_vantage': auth_config.get('alpha_vantage') or {},
            'open_weather_map': auth_config.get('open_weather_map' or {})
        }
        return auth_config


def _move_config_sections(user_config, local_config):
    """
    Temporary method to handle one-time migration of user_config params to local_config
    Args:
        user_config (NGIConfig): user configuration object
        local_config (NGIConfig): local configuration object
    """
    depreciated_user_configs = ("interface", "listener", "skills", "session", "tts", "stt", "logs", "device")
    try:
        if any([d in user_config.content for d in depreciated_user_configs]):
            LOG.warning("Depreciated keys found in user config! Adding them to local config")
            if "wake_words_enabled" in user_config.content.get("interface", dict()):
                user_config["interface"]["wake_word_enabled"] = user_config["interface"].pop("wake_words_enabled")
            config_to_move = {"interface": user_config.content.pop("interface", {}),
                              "listener": user_config.content.pop("listener", {}),
                              "skills": user_config.content.pop("skills", {}),
                              "session": user_config.content.pop("session", {}),
                              "tts": user_config.content.pop("tts", {}),
                              "stt": user_config.content.pop("stt", {}),
                              "logs": user_config.content.pop("logs", {}),
                              "device": user_config.content.pop("device", {})}
            local_config.update_keys(config_to_move)

        if not local_config.get("language"):
            local_config["language"] = dict()
        if local_config.get("stt", {}).get("detection_module"):
            local_config["language"]["detection_module"] = local_config["stt"].pop("detection_module")
        if local_config.get("stt", {}).get("translation_module"):
            local_config["language"]["translation_module"] = local_config["stt"].pop("translation_module")
    except (KeyError, RuntimeError):
        # If some other instance moves these values, just pass
        pass


def _get_neon_local_config(path: Optional[str] = None) -> NGIConfig:
    """
    Returns a dict local configuration and handles any
     migration of configuration values to local config from user config
    Args:
        path: optional path to directory containing yml configuration files
    Returns:
        NGIConfig object with local config
    """
    import inspect
    call = inspect.stack()[1]
    module = inspect.getmodule(call.frame)
    name = module.__name__ if module else call.filename
    LOG.warning("This reference is deprecated - "
                f"{name}:{call.lineno}")
    try:
        if isfile(join(path or get_config_dir(), "ngi_local_conf.yml")):
            local_config = NGIConfig("ngi_local_conf", path)
        else:
            local_config = NGIConfig("ngi_local_conf", "/tmp/neon")
    except PermissionError:
        LOG.error(f"Insufficient Permissions for path: {path}")
        local_config = NGIConfig("ngi_local_conf")
    _populate_read_only_config(path, basename(local_config.file_path),
                               local_config)

    if len(local_config.content) == 0:
        LOG.info(f"Created Empty Local Config at {local_config.path}")

    if isfile(join(path or get_config_dir(), "ngi_user_info.yml")):
        user_config = NGIConfig("ngi_user_info", path)
        _move_config_sections(user_config, local_config)

    # local_config.make_equal_by_keys(default_local_config.content)
    # LOG.info(f"Loaded local config from {local_config.file_path}")
    return local_config


def _populate_read_only_config(path: Optional[str], config_filename: str,
                               loaded_config: NGIConfig) -> bool:
    """
    Check if a requested config file wasn't loaded due to insufficient write
    permissions and duplicate its contents into the loaded config object.
    :param path: Optional requested RO config path
    :param config_filename: basename of the requested and loaded config file
    :param loaded_config: Loaded config object to populate with RO config
    :return: True if RO config was copied to new location, else False
    """
    # Handle reading unwritable config contents into new empty config
    requested_file = \
        os.path.abspath(join(path or
                             expanduser(os.getenv("NEON_CONFIG_PATH", "")),
                             config_filename))
    if os.path.isfile(requested_file) and \
            loaded_config.file_path != requested_file and \
            loaded_config.content == dict():
        LOG.warning(f"Loading requested file contents ({requested_file}) "
                    f"into {loaded_config.file_path}")
        with loaded_config.lock:
            shutil.copy(requested_file, loaded_config.file_path)
        loaded_config.check_for_updates()
        return True
    return False
