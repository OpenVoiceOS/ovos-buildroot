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

import os
import logging

from datetime import datetime, timedelta
from enum import Enum
from os.path import isdir
from typing import Optional, Union
from ovos_utils.xdg_utils import xdg_data_home
from ovos_utils.log import LOG


_LOG = None


def get_log_dir(config: dict = None) -> str:
    """
    Get log directory from configuration or default path, create if not exists
    """
    from ovos_config.config import Configuration
    config = config or Configuration()
    log_dir = os.path.expanduser(config.get("log_dir") or
                                 os.path.join(xdg_data_home(), "neon", "logs"))
    if not isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    return log_dir


class ServiceLog(Enum):
    SPEECH = "voice.log"
    SKILLS = "skills.log"
    AUDIO = "audio.log"
    ENCLOSURE = "enclosure.log"
    BUS = "bus.log"
    GUI = "gui.log"
    DISPLAY = "display.log"
    SERVER = "server.log"
    CLIENT = "client.log"
    OTHER = "extras.log"


def remove_old_logs(log_dir: str = None,
                    history_to_retain: timedelta = timedelta(weeks=6)):
    """
    Removes archived logs older than the specified history timedelta
    Args:
        log_dir: Path to archived logs
        history_to_retain: Timedelta of history to retain
    """
    from shutil import rmtree
    log_dir = log_dir or get_log_dir()
    for archive in os.listdir(log_dir):
        archive_path = os.path.join(log_dir, archive)
        if not os.path.isdir(archive_path):
            continue
        if datetime.now() - datetime.fromtimestamp(os.path.getmtime(
                archive_path)) > history_to_retain:
            LOG.info(f"removing {archive}")
            rmtree(archive_path)


def archive_logs(log_dir: str = None, archive_dir: Optional[str] = None):
    """
    Archives the logs in the specified log_dir to log_dir/dir_name
    Args:
        log_dir: Path to log files to be archived
        archive_dir: Directory to archive logs to (defaults to formatted time)
    """
    from glob import glob
    from os.path import join, basename
    from os import makedirs
    from shutil import move
    log_dir = log_dir or get_log_dir()
    default_dirname = "logs--" + datetime.now().strftime("%Y-%m-%d--%H:%M:%S")
    archive_dir = join(log_dir, archive_dir or default_dirname)
    makedirs(archive_dir, exist_ok=True)
    for file in glob(join(log_dir, "*.log")):
        if basename(file) != "start.log":
            move(file, archive_dir)


def get_logger(log_name: str, log_dir: str = None,
               std_out: bool = False) -> logging.Logger:
    """
    Get a logger with the specified name and write to the specified log_dir
    and optionally std_out
    Args:
        log_name: Name of log (also used as log filename)
        log_dir: Directory to write log file to
        std_out: Flag to include logs in STDOUT

    Returns:
        Logger with the specified handlers
    """
    log_dir = log_dir or get_log_dir()
    LOG.init({"path": log_dir or "stdout"})
    LOG.name = log_name
    log = LOG.create_logger(log_name, std_out)
    return log


def get_log_file_for_module(module_name: Union[str, list]) -> str:
    """
    Gets the default log path for the requested module
    Args:
        module_name: Runnable argument passed to Popen
            (i.e. neon_speech_client, [python3, -m, mycroft.skills])

    Returns:
        Path to logfile
    """
    if isinstance(module_name, list):
        module_name = module_name[-1]
    if module_name.startswith("neon_speech"):
        log_name = "voice.log"
    elif module_name.startswith("neon_audio"):
        log_name = "audio.log"
    elif module_name.startswith("neon_enclosure"):
        log_name = "enclosure.log"
    elif any(x for x in ("neon_messagebus", "neon_core.messagebus",
                         "mycroft.messagebus") if module_name.startswith(x)):
        log_name = "bus.log"
    elif any(x for x in ("neon_skills", "neon_core.skills",
                         "mycroft.skills") if module_name.startswith(x)):
        log_name = "skills.log"
    elif any(x for x in ("neon_gui",
                         "neon_core.gui") if module_name.startswith(x)):
        log_name = "display.log"
    elif module_name == "neon_core_client":
        log_name = "client.log"
    elif module_name == "neon_core_server":
        log_name = "server.log"
    elif module_name == "mycroft-gui-app":
        log_name = "gui.log"
    else:
        log_name = "extras.log"

    return os.path.join(get_log_dir(), log_name)


def init_log_for_module(service: ServiceLog = ServiceLog.OTHER,
                        std_out: bool = False, max_bytes: int = 50000000,
                        backup_count: int = 3, level: str = logging.DEBUG):
    """
    Initialize `LOG` singleton for the specified service in this thread
    Args:
        service: service requesting a logger object
        std_out: if true, print logs to std_out instead of to files
        max_bytes: maximum size in bytes allowed for this log file
        backup_count: number of archived logs to save
        level: minimum log level to filter to
    """
    if not isdir(get_log_dir()):
        LOG.info(f"Creating log directory: {get_log_dir()}")
        os.makedirs(get_log_dir())
    log_file = "stdout" if std_out else os.path.join(get_log_dir(),
                                                     service.value)
    LOG.init({"path": log_file,
              "max_bytes": max_bytes,
              "backup_count": backup_count,
              "level": level})


def init_log(config: dict = None, log_name: str = None) -> type(LOG):
    """
    Initialize `LOG` with configuration params. Should be called once on module
    init.
    :param config: Configuration to apply to LOG
    :param log_name: Optional LOG.name override, else use Configuration or default
    :returns: LOG singleton
    """
    from ovos_config.config import Configuration
    _cfg = config or Configuration()
    _log_level = _cfg.get("log_level", "INFO")
    _logs_conf = _cfg.get("logs") or {}
    _logs_conf["level"] = _log_level
    LOG.name = log_name or _logs_conf.get("name") or "neon-utils"
    LOG.debug(f"Initializing logger with: {_logs_conf}")
    LOG.init(_logs_conf)  # read log level from config
    overrides = _logs_conf.get('level_overrides') or {}
    for log in overrides.get("error") or []:
        logging.getLogger(log).setLevel(logging.ERROR)
    for log in overrides.get("warning") or []:
        logging.getLogger(log).setLevel(logging.WARNING)
    for log in overrides.get("info") or []:
        logging.getLogger(log).setLevel(logging.INFO)
    for log in overrides.get("debug") or []:
        logging.getLogger(log).setLevel(logging.DEBUG)
    return LOG


def get_log() -> type(LOG):
    """
    Return an initialized `LOG` object
    """
    global _LOG
    if not _LOG:
        _LOG = init_log()
    return _LOG
