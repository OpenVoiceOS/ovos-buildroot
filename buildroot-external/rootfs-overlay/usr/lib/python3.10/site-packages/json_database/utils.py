import json
from difflib import SequenceMatcher


class DummyLock:
    """ A fake lock.

    Arguments:
        path (str): path to the lockfile for the lock
    """
    def __init__(self, path=""):
        self.path = path

    def acquire(self, blocking=True):
        """ Acquire lock, locks thread and process lock.

        Arguments:
            blocking(bool): Set's blocking mode of acquire operation.
                            Default True.

        Returns: True if lock succeeded otherwise False
        """
        return True

    def release(self):
        """ Release acquired lock. """
        pass

    def __enter__(self):
        """ Context handler, acquires lock in blocking mode. """
        return self

    def __exit__(self, _type, value, traceback):
        """ Releases the lock. """
        pass


def fuzzy_match(x, against):
    """Perform a 'fuzzy' comparison between two strings.
    Returns:
        float: match percentage -- 1.0 for perfect match,
               down to 0.0 for no match at all.
    """
    return SequenceMatcher(None, x, against).ratio()


def match_one(query, choices):
    """
        Find best match from a list or dictionary given an input

        Arguments:
            query:   string to test
            choices: list or dictionary of choices

        Returns: tuple with best match, score
    """
    if isinstance(choices, dict):
        _choices = list(choices.keys())
    elif isinstance(choices, list):
        _choices = choices
    else:
        raise ValueError('a list or dict of choices must be provided')

    best = (_choices[0], fuzzy_match(query, _choices[0]))
    for c in _choices[1:]:
        score = fuzzy_match(query, c)
        if score > best[1]:
            best = (c, score)

    if isinstance(choices, dict):
        return (choices[best[0]], best[1])
    else:
        return best


def merge_dict(base, delta, merge_lists=True, skip_empty=True,
               no_dupes=True, new_only=False):
    """
        Recursively merging configuration dictionaries.

        Args:
            base:  Target for merge
            delta: Dictionary to merge into base
            merge_lists: if a list is found merge contents instead of replacing
            skip_empty: if an item in delta is empty, dont overwrite base
            no_dupes: when merging lists deduplicate entries
            new_only: only merge keys not yet in base
    """

    for k, d in delta.items():
        b = base.get(k)
        if isinstance(d, dict) and isinstance(b, dict):
            merge_dict(b, d, merge_lists, skip_empty, no_dupes, new_only)
        else:
            if new_only and k in base:
                continue
            if skip_empty and not d and d is not False:
                # dont replace if new entry is empty
                pass
            elif all((isinstance(b, list), isinstance(d, list), merge_lists)):
                if no_dupes:
                    base[k] += [item for item in d if item not in base[k]]
                else:
                    base[k] += d
            else:
                base[k] = d
    return base


def load_commented_json(filename):
    """ Loads an JSON file, ignoring comments

    Supports a trivial extension to the JSON file format.  Allow comments
    to be embedded within the JSON, requiring that a comment be on an
    independent line starting with '//' or '#'.

    NOTE: A file created with these style comments will break strict JSON
          parsers.  This is similar to but lighter-weight than "human json"
          proposed at https://hjson.org

    Args:
        filename (str):  path to the commented JSON file

    Returns:
        obj: decoded Python object
    """
    with open(filename, encoding='utf-8') as f:
        contents = f.read()

    return json.loads(uncomment_json(contents))


def uncomment_json(commented_json_str):
    """ Removes comments from a JSON string.

    Supporting a trivial extension to the JSON format.  Allow comments
    to be embedded within the JSON, requiring that a comment be on an
    independent line starting with '//' or '#'.

    Example...
       {
         // comment
         'name' : 'value'
       }

    Args:
        commented_json_str (str):  a JSON string

    Returns:
        str: uncommented, legal JSON
    """
    lines = commented_json_str.splitlines()
    # remove all comment lines, starting with // or #
    nocomment = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("#"):
            continue
        nocomment.append(line)

    return " ".join(nocomment)


def is_jsonifiable(thing):
    if not isinstance(thing, dict):
        if isinstance(thing, str):
            try:
                json.loads(thing)
                return True
            except:
                pass
        else:
            try:
                thing.__dict__
                return True
            except:
                pass
        return False
    return True


def get_key_recursively(search_dict, field, filter_None=True):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    if not is_jsonifiable(search_dict):
        raise ValueError("unparseable format")
    fields_found = []

    for key, value in search_dict.items():
        if value is None and filter_None:
            continue
        if key == field:
            fields_found.append(search_dict)

        elif isinstance(value, dict):
            fields_found += get_key_recursively(value, field, filter_None)

        elif isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    try:
                        if get_key_recursively(item.__dict__, field, filter_None):
                            fields_found.append(item)
                    except:
                        continue  # can't parse
                else:
                    fields_found += get_key_recursively(item, field, filter_None)

    return fields_found


def get_key_recursively_fuzzy(search_dict, field, thresh=0.6, filter_None=True):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    if not is_jsonifiable(search_dict):
        raise ValueError("unparseable format")

    fields_found = []

    for key, value in search_dict.items():
        if value is None and filter_None:
            continue
        score = 0
        if isinstance(key, str):
            score = fuzzy_match(key, field)

        if score >= thresh:
            fields_found.append((search_dict, score))
        elif isinstance(value, dict):
            fields_found += get_key_recursively_fuzzy(value, field, thresh, filter_None)

        elif isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    try:
                        if get_key_recursively_fuzzy(item.__dict__, field, thresh, filter_None):
                            fields_found.append((item, score))
                    except:
                        continue  # can't parse
                else:
                    fields_found += get_key_recursively_fuzzy(item, field, thresh, filter_None)
    return sorted(fields_found, key = lambda i: i[1],reverse=True)


def get_value_recursively(search_dict, field, target_value):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    if not is_jsonifiable(search_dict):
        raise ValueError("unparseable format")
    fields_found = []

    for key, value in search_dict.items():

        if key == field and value == target_value:
            fields_found.append(search_dict)

        elif isinstance(value, dict):
            fields_found += get_value_recursively(value, field, target_value)

        elif isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    try:
                        if get_value_recursively(item.__dict__, field, target_value):
                            fields_found.append(item)
                    except:
                        continue  # can't parse
                else:
                    fields_found += get_value_recursively(item, field, target_value)

    return fields_found


def get_value_recursively_fuzzy(search_dict, field, target_value, thresh=0.6):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    if not is_jsonifiable(search_dict):
        raise ValueError("unparseable format")
    fields_found = []
    for key, value in search_dict.items():
        if key == field:
            if isinstance(value, str):
                score = fuzzy_match(target_value, value)
                if score >= thresh:
                    fields_found.append((search_dict, score))
            elif isinstance(value, list):
                for item in value:
                    score = fuzzy_match(target_value, item)
                    if score >= thresh:
                        fields_found.append((search_dict, score))
        elif isinstance(value, dict):
            fields_found += get_value_recursively_fuzzy(value, field, target_value, thresh)

        elif isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    try:
                        found = get_value_recursively_fuzzy(item.__dict__, field, target_value, thresh)
                        if len(found):
                            fields_found.append((item, found[0][1]))
                    except:
                        continue  # can't parse
                else:
                    fields_found += get_value_recursively_fuzzy(item, field, target_value, thresh)

    return sorted(fields_found, key = lambda i: i[1],reverse=True)


def jsonify_recursively(thing):
    if isinstance(thing, list):
        jsonified = list(thing)
        for idx, item in enumerate(thing):
            jsonified[idx] = jsonify_recursively(item)
    elif isinstance(thing, dict):
        try:
            # can't import at top level to do proper check
            jsonified = dict(thing.db)
        except:
            jsonified = dict(thing)
        for key in jsonified.keys():
            value = jsonified[key]
            jsonified[key] = jsonify_recursively(value)
    else:
        try:
            jsonified = thing.__dict__
        except:
            jsonified = thing
    return jsonified
