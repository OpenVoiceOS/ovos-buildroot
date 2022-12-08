import tempfile
import time

import os
import os.path


from ovos_utils.log import LOG


def get_ipc_directory(domain=None, config=None):
    """Get the directory used for Inter Process Communication

    Files in this folder can be accessed by different processes on the
    machine.  Useful for communication.  This is often a small RAM disk.

    Args:
        domain (str): The IPC domain.  Basically a subdirectory to prevent
            overlapping signal filenames.
        config (dict): mycroft.conf, to read ipc directory from

    Returns:
        str: a path to the IPC directory
    """
    if config is None:
        from ovos_config.config import read_mycroft_config
        config = read_mycroft_config()
    path = config.get("ipc_path")
    if not path:
        # If not defined, use /tmp/mycroft/ipc
        path = os.path.join(tempfile.gettempdir(), "mycroft", "ipc")
    return ensure_directory_exists(path, domain)


def ensure_directory_exists(directory, domain=None):
    """ Create a directory and give access rights to all

    Args:
        domain (str): The IPC domain.  Basically a subdirectory to prevent
            overlapping signal filenames.

    Returns:
        str: a path to the directory
    """
    if domain:
        directory = os.path.join(directory, domain)

    # Expand and normalize the path
    directory = os.path.normpath(directory)
    directory = os.path.expanduser(directory)

    if not os.path.isdir(directory):
        try:
            save = os.umask(0)
            os.makedirs(directory, 0o777)  # give everyone rights to r/w here
        except OSError:
            LOG.warning("Failed to create: " + directory)
            pass
        finally:
            os.umask(save)

    return directory


def create_file(filename):
    """ Create the file filename and create any directories needed

        Args:
            filename: Path to the file to be created
    """
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with open(filename, 'w') as f:
        f.write('')


def create_signal(signal_name, config=None):
    """Create a named signal

    Args:
        signal_name (str): The signal's name.  Must only contain characters
            valid in filenames.
        config (dict): mycroft.conf, to read ipc directory from
    """
    try:
        path = os.path.join(get_ipc_directory(config=config),
                            "signal", signal_name)
        create_file(path)
        return os.path.isfile(path)
    except IOError:
        return False


def check_for_signal(signal_name, sec_lifetime=0, config=None):
    """See if a named signal exists

    Args:
        signal_name (str): The signal's name.  Must only contain characters
            valid in filenames.
        sec_lifetime (int, optional): How many seconds the signal should
            remain valid.  If 0 or not specified, it is a single-use signal.
            If -1, it never expires.
        config (dict): mycroft.conf, to read ipc directory from

    Returns:
        bool: True if the signal is defined, False otherwise
    """
    path = os.path.join(get_ipc_directory(config=config),
                        "signal", signal_name)
    if os.path.isfile(path):
        if sec_lifetime == 0:
            # consume this single-use signal
            os.remove(path)
        elif sec_lifetime == -1:
            return True
        elif int(os.path.getctime(path) + sec_lifetime) < int(time.time()):
            # remove once expired
            os.remove(path)
            return False
        return True

    # No such signal exists
    return False
