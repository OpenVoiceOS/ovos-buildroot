from ovos_utils.log import LOG
from os.path import exists, join, dirname
import os
import sys
from subprocess import PIPE, Popen
from typing import Optional, Union
from pako import PakoManager
from ovos_skills_manager.exceptions import PipException, \
    SkillRequirementsException, InvalidManifest
from combo_lock import ComboLock
from tempfile import gettempdir
import yaml

# default constraints to use if none are given
DEFAULT_CONSTRAINTS = '/etc/mycroft/constraints.txt'
PIP_LOCK = ComboLock(join(gettempdir(), "ovos_pip.lock"))


def pip_install(packages:list, constraints:Optional[str]=None, print_logs:bool=False):
    if not len(packages):
        return False
    # Use constraints to limit the installed versions
    if constraints and not exists(constraints):
        LOG.error('Couldn\'t find the constraints file')
        return False
    elif exists(DEFAULT_CONSTRAINTS):
        constraints = DEFAULT_CONSTRAINTS

    can_pip = os.access(dirname(sys.executable), os.W_OK | os.X_OK)
    pip_args = [sys.executable, '-m', 'pip', 'install']
    if constraints:
        pip_args += ['-c', constraints]

    if not can_pip:
        pip_args = ['sudo', '-n'] + pip_args

    with PIP_LOCK:
        """
        Iterate over the individual Python packages and
        install them one by one to enforce the order specified
        in the manifest.
        """
        for dependent_python_package in packages:
            LOG.info("(pip) Installing " + dependent_python_package)
            pip_command = pip_args + [dependent_python_package]
            if print_logs:
                proc = Popen(pip_command)
            else:
                proc = Popen(pip_command, stdout=PIPE, stderr=PIPE)
            pip_code = proc.wait()
            if pip_code != 0:
                stderr = proc.stderr.read().decode()
                raise PipException(
                    pip_code, proc.stdout.read().decode(), stderr
                )

    return True


def install_system_deps(manifest:dict, overrides:Optional[dict]=None):
    overrides = overrides or {
        exe: (packages or '').split()
        for exe, packages in manifest.items()
    }
    packages = overrides.pop('all', [])
    if not len(packages):
        return False
    try:
        manager = PakoManager()
        return manager.install(packages, overrides=overrides)
    except Exception as e:
        raise SkillRequirementsException(str(e))


def validate_manifest(content:Union[str,dict]):
    if isinstance(content, str):
        data = yaml.safe_load(content)
    else:
        assert isinstance(content, dict)
        data = content
    if not data:
        # most likely just the template full of comments
        raise InvalidManifest
    if 'dependencies' in data:
        return data

    # some skills in the wild have the manifest without the top-level key
    LOG.warning("invalid manifest, attempting recovery")
    recovered = {"dependencies": {}}
    if "python" in data:
        recovered["dependencies"]["python"] = data["python"]
    if "skill" in data:
        recovered["dependencies"]["skill"] = data["skill"]
    if "system" in data:
        recovered["dependencies"]["system"] = data["system"]
    if not len(recovered["dependencies"]):
        # suspicious, doesn't follow standard
        raise InvalidManifest
    return recovered
