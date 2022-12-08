import json
import logging
from os import makedirs, remove
from os.path import expanduser, isdir, dirname, exists, isfile, join
from pprint import pprint
from tempfile import gettempdir

from combo_lock import ComboLock

from json_database.exceptions import InvalidItemID, DatabaseNotCommitted, \
    SessionError, MatchError
from json_database.utils import DummyLock, load_commented_json, merge_dict, \
    jsonify_recursively, get_key_recursively, get_key_recursively_fuzzy, \
    get_value_recursively_fuzzy, get_value_recursively
from json_database.xdg_utils import xdg_cache_home, xdg_data_home, xdg_config_home

LOG = logging.getLogger("JsonDatabase")
LOG.setLevel("INFO")


class JsonStorage(dict):
    """
    persistent python dict
    """

    def __init__(self, path, disable_lock=False):
        super().__init__()
        lock_path = join(gettempdir(), path.split("/")[-1] + ".lock")
        if disable_lock:
            self.lock = DummyLock(lock_path)
        else:
            self.lock = ComboLock(lock_path)
        self.path = path
        if self.path:
            self.load_local(self.path)

    def load_local(self, path):
        """
            Load local json file into self.

            Args:
                path (str): file to load
        """
        with self.lock:
            path = expanduser(path)
            if exists(path) and isfile(path):
                self.clear()
                try:
                    config = load_commented_json(path)
                    for key in config:
                        self[key] = config[key]
                    LOG.debug("Json {} loaded".format(path))
                except Exception as e:
                    LOG.error("Error loading json '{}'".format(path))
                    LOG.error(repr(e))
            else:
                LOG.debug("Json '{}' not defined, skipping".format(path))

    def clear(self):
        for k in dict(self):
            self.pop(k)

    def reload(self):
        if exists(self.path) and isfile(self.path):
            self.load_local(self.path)
        else:
            raise DatabaseNotCommitted

    def store(self, path=None):
        """
            store the json db locally.
        """
        with self.lock:
            path = path or self.path
            if not path:
                LOG.warning("json db path not set")
                return
            path = expanduser(path)
            if dirname(path) and not isdir(dirname(path)):
                makedirs(dirname(path))
            with open(path, 'w', encoding="utf-8") as f:
                json.dump(self, f, indent=4, ensure_ascii=False)

    def remove(self):
        with self.lock:
            if isfile(self.path):
                remove(self.path)

    def merge(self, conf, merge_lists=True, skip_empty=True, no_dupes=True,
              new_only=False):
        merge_dict(self, conf, merge_lists, skip_empty, no_dupes, new_only)
        return self

    def __enter__(self):
        """ Context handler """
        return self

    def __exit__(self, _type, value, traceback):
        """ Commits changes and Closes the session """
        try:
            self.store()
        except Exception as e:
            LOG.error(e)
            raise SessionError


class JsonDatabase(dict):
    """ searchable persistent dict """

    def __init__(self,
                 name,
                 path=None,
                 disable_lock=False,
                 extension="json"):
        super().__init__()
        self.name = name
        self.path = path or f"{name}.{extension}"
        self.db = JsonStorage(self.path, disable_lock=disable_lock)
        self.db[name] = []
        self.db.load_local(self.path)

    # operator overloads
    def __enter__(self):
        """ Context handler """
        return self

    def __exit__(self, _type, value, traceback):
        """ Commits changes and Closes the session """
        try:
            self.commit()
        except Exception as e:
            LOG.error(e)
            raise SessionError

    def __repr__(self):
        return str(jsonify_recursively(self))

    def __len__(self):
        return len(self.db.get(self.name, []))

    def __getitem__(self, item):
        if not isinstance(item, int):
            try:
                item_id = int(item)
            except Exception as e:
                item_id = self.get_item_id(item)
                if item_id < 0:
                    raise InvalidItemID
        else:
            item_id = item
        if item_id >= len(self.db[self.name]):
            raise InvalidItemID
        return self.db[self.name][item_id]

    def __setitem__(self, item_id, value):
        if not isinstance(item_id, int) or item_id >= len(self) or item_id < 0:
            raise InvalidItemID
        else:
            self.update_item(item_id, value)

    def __iter__(self):
        for item in self.db[self.name]:
            yield item

    def __contains__(self, item):
        item = jsonify_recursively(item)
        return item in self.db[self.name]

    # database
    def commit(self):
        """
            store the json db locally.
        """
        self.db.store(self.path)

    def reset(self):
        self.db.reload()

    def print(self):
        pprint(jsonify_recursively(self))

    # item manipulations
    def append(self, value):
        value = jsonify_recursively(value)
        self.db[self.name].append(value)
        return len(self)

    def add_item(self, value, allow_duplicates=False):
        """ add an item to database
         if allow_duplicates is True, item is added unconditionally,
         else only if no exact match is present
         """
        if allow_duplicates or value not in self:
            self.append(value)
            return len(self)
        return self.get_item_id(value)

    def match_item(self, value, match_strategy=None):
        """ match value to some item in database
        returns a list of matched items
        """
        value = jsonify_recursively(value)
        matches = []
        for idx, item in enumerate(self):

            # TODO match strategy
            # - require exact match
            # - require list of keys to match
            # - require at least one of key list to match
            # - require at exactly one of key list to match

            # by default check for exact matches
            if item == value:
                matches.append((item, idx))

        return matches

    def merge_item(self, value, item_id=None, match_strategy=None,
                   merge_strategy=None):
        """ search an item according to match criteria, merge fields"""
        if item_id is None:
            matches = self.match_item(value, match_strategy)
            if not matches:
                raise MatchError
            match, item_id = matches[0][1]
        else:
            match = self[item_id]
        # TODO merge strategy
        # - only merge some keys
        # - dont merge some keys
        # - merge all keys
        # - dont overwrite keys
        value = jsonify_recursively(value)
        self[item_id] = merge_dict(match, value)

    def replace_item(self, value, item_id=None, match_strategy=None):
        """ search an item according to match criteria, replace it"""
        if item_id is None:
            matches = self.match_item(value, match_strategy)
            if not matches:
                raise MatchError
            match, item_id = matches[0][1]
        value = jsonify_recursively(value)
        self[item_id] = value

    # item_id
    def get_item_id(self, item):
        """
        item_id is simply the index of the item in the database
        WARNING: this is not immutable across sessions
        """
        for match, idx in self.match_item(item):
            return idx
        return -1

    def update_item(self, item_id, new_item):
        """
        item_id is simply the index of the item in the database
        WARNING: this is not immutable across sessions
        """
        new_item = jsonify_recursively(new_item)
        self.db[self.name][item_id] = new_item

    def remove_item(self, item_id):
        """
        item_id is simply the index of the item in the database
        WARNING: this is not immutable across sessions
        """
        return self.db[self.name].pop(item_id)

    # search
    def search_by_key(self, key, fuzzy=False, thresh=0.7, include_empty=False):
        if fuzzy:
            return get_key_recursively_fuzzy(self.db, key, thresh, not include_empty)
        return get_key_recursively(self.db, key, not include_empty)

    def search_by_value(self, key, value, fuzzy=False, thresh=0.7):
        if fuzzy:
            return get_value_recursively_fuzzy(self.db, key, value, thresh)
        return get_value_recursively(self.db, key, value)


# XDG aware classes

class JsonStorageXDG(JsonStorage):
    """ xdg respectful persistent dicts """

    def __init__(self,
                 name,
                 xdg_folder=xdg_cache_home(),
                 disable_lock=False, subfolder="json_database",
                 extension="json"):
        self.name = name
        path = join(xdg_folder, subfolder, f"{name}.{extension}")
        super().__init__(path, disable_lock=disable_lock)


class JsonDatabaseXDG(JsonDatabase):
    """ xdg respectful json database """

    def __init__(self, name, xdg_folder=xdg_data_home(),
                 disable_lock=False, subfolder="json_database",
                 extension="jsondb"):
        path = join(xdg_folder, subfolder, f"{name}.{extension}")
        super().__init__(name, path, disable_lock=disable_lock, extension=extension)


class JsonConfigXDG(JsonStorageXDG):
    """ xdg respectful config files, using json_storage.JsonStorageXDG """

    def __init__(self, name, xdg_folder=xdg_config_home(),
                 disable_lock=False, subfolder="json_database",
                 extension="json"):
        super().__init__(name, xdg_folder, disable_lock, subfolder, extension)
