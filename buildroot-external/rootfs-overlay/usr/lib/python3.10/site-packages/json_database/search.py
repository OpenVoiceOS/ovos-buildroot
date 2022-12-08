from json_database.utils import fuzzy_match, match_one
from json_database import JsonDatabase


class Query:
    def __init__(self, db):
        if isinstance(db, JsonDatabase):
            self.result = list(db)
        else:
            self.result = [db]

    def contains_key(self, key, fuzzy=False, thresh=0.7, ignore_case=False):
        if fuzzy:
            after = []
            for e in self.result:
                filter = True
                for k in e:
                    if ignore_case:
                        score = fuzzy_match(k.lower(), key.lower())
                    else:
                        score = fuzzy_match(k, key)
                    if score < thresh:
                        continue
                    filter = False
                if not filter:
                    after.append(e)
            self.result = after
        elif ignore_case:
            self.result = [a for a in self.result
                           if a.get(key) or a.get(key.lower())]
        else:
            self.result = [a for a in self.result if a.get(key)]
        return self

    def contains_value(self, key, value, fuzzy=False, thresh=0.75, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        if fuzzy:
            after = []
            for e in self.result:
                if isinstance(e[key], str):
                    if ignore_case:
                        score = fuzzy_match(value.lower(), e[key].lower())
                    else:
                        score = fuzzy_match(value, e[key])
                    if score > thresh:
                        after.append(e)
                elif isinstance(e[key], list):
                    if ignore_case:
                        v, score = match_one(value.lower(),
                                             [_.lower() for _ in e[key]])
                    else:
                        v, score = match_one(value, e[key])
                    if score < thresh:
                        continue
                    after.append(e)
                elif isinstance(e[key], dict):
                    if ignore_case:
                        v, score = match_one(value.lower(),
                                             [_.lower() for _ in e[key].keys()])
                    else:
                        v, score = match_one(value, e[key])
                    if score < thresh:
                        continue
                    after.append(e)
            self.result = after
        elif ignore_case and isinstance(value, str):
            after = []
            for a in self.result:
                if isinstance(a[key], str) and value.lower() in a[key].lower():
                    after.append(a)
                elif value.lower() in a[key] or value in a[key]:
                    after.append(a)
            self.result = after
        else:
            self.result = [a for a in self.result if value in a[key]]
        return self

    def value_contains(self, key, value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        if ignore_case:
            after = []
            value = str(value).lower()
            for e in self.result:
                if isinstance(e[key], str) and ignore_case:
                    if value.lower() in e[key].lower():
                        after.append(e)
                elif isinstance(e[key], list) and ignore_case:
                    if value.lower() in [str(_).lower() for _ in e[key]]:
                        after.append(e)
                elif isinstance(e[key], dict) and ignore_case:
                    if value.lower() in [str(_).lower() for _ in e[key].keys()]:
                        after.append(e)

                elif isinstance(e[key], str):
                    if value in e[key]:
                        after.append(e)
                elif isinstance(e[key], list):
                    if value in [str(_) for _ in e[key]]:
                        after.append(e)
                elif isinstance(e[key], dict):
                    if value in [str(_) for _ in e[key].keys()]:
                        after.append(e)

            self.result = after
        else:
            self.result = [e for e in self.result if value in e[key]]
        return self

    def value_contains_token(self, key, value, fuzzy=False, thresh=0.75, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        after = []
        value = str(value)
        for e in self.result:
            if isinstance(e[key], str):
                if fuzzy:
                    _, score = match_one(value.lower(),
                                         e[key].lower().split(" "))
                    if score > thresh:
                        after.append(e)
                elif ignore_case and value.lower() in e[key].lower().split(" "):
                    after.append(e)
                elif value in e[key].split(" "):
                    after.append(e)
            elif value in e[key]:
                after.append(e)
        self.result = after
        return self

    def equal(self, key, value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        if ignore_case and isinstance(value, str):
            self.result = [a for a in self.result
                           if a[key].lower() == value.lower()]
        else:
            self.result = [a for a in self.result if a[key] == value]
        return self

    def below(self, key, value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        self.result = [a for a in self.result if a[key] < value]
        return self

    def above(self, key, value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        self.result = [a for a in self.result if a[key] > value]
        return self

    def below_or_equal(self, key, value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        self.result = [a for a in self.result if a[key] <= value]
        return self

    def above_or_equal(self, key, value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        self.result = [a for a in self.result if a[key] >= value]
        return self

    def in_range(self, key, min_value, max_value, ignore_case=False):
        self.contains_key(key, ignore_case=ignore_case)
        self.result = [a for a in self.result if min_value < a[key] < max_value]
        return self

    def all(self):
        return self

    def build(self):
        return self.result


