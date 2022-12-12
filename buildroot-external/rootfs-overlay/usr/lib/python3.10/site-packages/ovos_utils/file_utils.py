import collections
import csv
import re
import os
from os import walk
from os.path import splitext, join, dirname
import tempfile
from ovos_utils.bracket_expansion import expand_options
from ovos_utils.log import LOG
from ovos_utils.system import search_mycroft_core_location
import time
from os.path import dirname

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def get_temp_path(*args):
    """Generate a valid path in the system temp directory.

    This method accepts one or more strings as arguments. The arguments are
    joined and returned as a complete path inside the systems temp directory.
    Importantly, this will not create any directories or files.

    Example usage: get_temp_path('mycroft', 'audio', 'example.wav')
    Will return the equivalent of: '/tmp/mycroft/audio/example.wav'

    Args:
        path_element (str): directories and/or filename

    Returns:
        (str) a valid path in the systems temp directory
    """
    try:
        path = os.path.join(tempfile.gettempdir(), *args)
    except TypeError:
        raise TypeError("Could not create a temp path, get_temp_path() only "
                        "accepts Strings")
    return path


def get_cache_directory(folder):
    # optional import to use ram for cache
    # does not work in windows!
    path = get_temp_path(folder)
    if os.name != 'nt':
        try:
            from memory_tempfile import MemoryTempfile
            path = join(MemoryTempfile(fallback=True).gettempdir(), folder)
        except ImportError:
            pass
        except Exception as e:
            LOG.exception(e)
    os.makedirs(path, exist_ok=True)
    return path


def resolve_ovos_resource_file(res_name):
    """Convert a resource into an absolute filename.
    used internally for ovos resources
    """
    # First look for fully qualified file (e.g. a user setting)
    if os.path.isfile(res_name):
        return res_name

    # now look in bundled ovos resources
    filename = join(dirname(__file__), "res", res_name)
    if os.path.isfile(filename):
        return filename

    # let's look in mycroft/ovos-core if it's installed
    path = search_mycroft_core_location()
    if path:
        filename = join(path, "mycroft", "res", res_name)
        if os.path.isfile(filename):
            return filename
    return None  # Resource cannot be resolved


def resolve_resource_file(res_name, root_path=None, config=None):
    """Convert a resource into an absolute filename.

    Resource names are in the form: 'filename.ext'
    or 'path/filename.ext'

    The system wil look for ~/.mycroft/res_name first, and
    if not found will look at /opt/mycroft/res_name,
    then finally it will look for res_name in the 'mycroft/res'
    folder of the source code package.

    Example:
    With mycroft running as the user 'bob', if you called
        resolve_resource_file('snd/beep.wav')
    it would return either '/home/bob/.mycroft/snd/beep.wav' or
    '/opt/mycroft/snd/beep.wav' or '.../mycroft/res/snd/beep.wav',
    where the '...' is replaced by the path where the package has
    been installed.

    Args:
        res_name (str): a resource path/name
        config (dict): mycroft.conf, to read data directory from
    Returns:
        str: path to resource or None if no resource found
    """
    if config is None:
        from ovos_config.config import read_mycroft_config
        config = read_mycroft_config()

    # First look for fully qualified file (e.g. a user setting)
    if os.path.isfile(res_name):
        return res_name

    # Now look for ~/.mycroft/res_name (in user folder)
    filename = os.path.expanduser("~/.mycroft/" + res_name)
    if os.path.isfile(filename):
        return filename

    # Next look for /opt/mycroft/res/res_name
    data_dir = os.path.expanduser(config.get('data_dir', "/opt/mycroft"))
    filename = os.path.expanduser(os.path.join(data_dir, res_name))
    if os.path.isfile(filename):
        return filename

    # look in ovos_utils package itself
    found = resolve_ovos_resource_file(res_name)
    if found:
        return found

    return None  # Resource cannot be resolved


def read_vocab_file(path):
    """ Read voc file.

        This reads a .voc file, stripping out empty lines comments and expand
        parentheses. It returns each line as a list of all expanded
        alternatives.

        Args:
            path (str): path to vocab file.

        Returns:
            List of Lists of strings.
    """
    vocab = []
    with open(path, 'r', encoding='utf8') as voc_file:
        for line in voc_file.readlines():
            if line.startswith('#') or line.strip() == '':
                continue
            vocab.append(expand_options(line.lower()))
    return vocab


def load_regex_from_file(path, skill_id):
    """Load regex from file
    The regex is sent to the intent handler using the message bus

    Args:
        path:       path to vocabulary file (*.voc)
        skill_id:   skill_id to the regex is tied to
    """
    from ovos_utils.intents.intent_service_interface import munge_regex

    regexes = []
    if path.endswith('.rx'):
        with open(path, 'r', encoding='utf8') as reg_file:
            for line in reg_file.readlines():
                if line.startswith("#"):
                    continue
                LOG.debug('regex pre-munge: ' + line.strip())
                regex = munge_regex(line.strip(), skill_id)
                LOG.debug('regex post-munge: ' + regex)
                # Raise error if regex can't be compiled
                try:
                    re.compile(regex)
                    regexes.append(regex)
                except Exception as e:
                    LOG.warning(f'Failed to compile regex {regex}: {e}')

    return regexes


def load_vocabulary(basedir, skill_id):
    """Load vocabulary from all files in the specified directory.

    Args:
        basedir (str): path of directory to load from (will recurse)
        skill_id: skill the data belongs to
    Returns:
        dict with intent_type as keys and list of list of lists as value.
    """
    from ovos_utils.intents.intent_service_interface import to_alnum

    vocabs = {}
    for path, _, files in walk(basedir):
        for f in files:
            if f.endswith(".voc"):
                vocab_type = to_alnum(skill_id) + splitext(f)[0]
                vocs = read_vocab_file(join(path, f))
                if vocs:
                    vocabs[vocab_type] = vocs
    return vocabs


def load_regex(basedir, skill_id):
    """Load regex from all files in the specified directory.

    Args:
        basedir (str): path of directory to load from
        bus (messagebus emitter): messagebus instance used to send the vocab to
                                  the intent service
        skill_id (str): skill identifier
    """
    regexes = []
    for path, _, files in walk(basedir):
        for f in files:
            if f.endswith(".rx"):
                regexes += load_regex_from_file(join(path, f), skill_id)
    return regexes


def read_value_file(filename, delim):
    """Read value file.

    The value file is a simple csv structure with a key and value.

    Args:
        filename (str): file to read
        delim (str): csv delimiter

    Returns:
        OrderedDict with results.
    """
    result = collections.OrderedDict()

    if filename:
        with open(filename) as f:
            reader = csv.reader(f, delimiter=delim)
            for row in reader:
                # skip blank or comment lines
                if not row or row[0].startswith("#"):
                    continue
                if len(row) != 2:
                    continue

                result[row[0]] = row[1]
    return result


def read_translated_file(filename, data):
    """Read a file inserting data.

    Args:
        filename (str): file to read
        data (dict): dictionary with data to insert into file

    Returns:
        list of lines.
    """
    if filename:
        with open(filename) as f:
            text = f.read().replace('{{', '{').replace('}}', '}')
            return text.format(**data or {}).rstrip('\n').split('\n')
    else:
        return None


class FileWatcher:
    def __init__(self, files, callback, recursive=False, ignore_creation=False):
        self.observer = Observer()
        self.handlers = []
        for file_path in files:
            watch_dir = dirname(file_path)
            self.observer.schedule(FileEventHandler(file_path, callback, ignore_creation),
                                   watch_dir, recursive=recursive)
        self.observer.start()

    def shutdown(self):
        self.observer.unschedule_all()
        self.observer.stop()


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, file_path, callback, ignore_creation=False):
        super().__init__()
        self._callback = callback
        self._file_path = file_path
        self._debounce = 1
        self._last_update = 0
        if ignore_creation:
            self._events = ('modified')
        else:
            self._events = ('created', 'modified')

    def on_any_event(self, event):
        if event.is_directory:
            return
        elif event.event_type in self._events:
            if event.src_path == self._file_path:
                if time.time() - self._last_update >= self._debounce:
                    self._callback(event.src_path)
                    self._last_update = time.time()
