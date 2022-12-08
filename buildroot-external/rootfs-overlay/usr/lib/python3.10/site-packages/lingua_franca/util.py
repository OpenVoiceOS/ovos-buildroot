from difflib import SequenceMatcher
from enum import IntEnum, auto

import rapidfuzz


class MatchStrategy(IntEnum):
    SIMPLE_RATIO = auto()
    RATIO = auto()
    PARTIAL_RATIO = auto()
    TOKEN_SORT_RATIO = auto()
    TOKEN_SET_RATIO = auto()
    PARTIAL_TOKEN_RATIO = auto()
    PARTIAL_TOKEN_SORT_RATIO = auto()
    PARTIAL_TOKEN_SET_RATIO = auto()


def fuzzy_match(x, against, strategy=MatchStrategy.SIMPLE_RATIO):
    """Perform a 'fuzzy' comparison between two strings.
    Returns:
        float: match percentage -- 1.0 for perfect match,
               down to 0.0 for no match at all.
    """
    if strategy == MatchStrategy.RATIO:
        score = rapidfuzz.fuzz.ratio(x, against) / 100
    elif strategy == MatchStrategy.PARTIAL_RATIO:
        score = rapidfuzz.fuzz.partial_ratio(x, against) / 100
    elif strategy == MatchStrategy.TOKEN_SORT_RATIO:
        score = rapidfuzz.fuzz.token_sort_ratio(x, against) / 100
    elif strategy == MatchStrategy.TOKEN_SET_RATIO:
        score = rapidfuzz.fuzz.token_set_ratio(x, against) / 100
    elif strategy == MatchStrategy.PARTIAL_TOKEN_SORT_RATIO:
        score = rapidfuzz.fuzz.partial_token_sort_ratio(x, against) / 100
    elif strategy == MatchStrategy.PARTIAL_TOKEN_SET_RATIO:
        score = rapidfuzz.fuzz.partial_token_set_ratio(x, against) / 100
    elif strategy == MatchStrategy.PARTIAL_TOKEN_RATIO:
        score = rapidfuzz.fuzz.partial_token_ratio(x, against) / 100
    else:
        score = SequenceMatcher(None, x, against).ratio()

    return score


def match_one(query, choices, match_func=None, strategy=MatchStrategy.SIMPLE_RATIO):
    """
        Find best match from a list or dictionary given an input

        Arguments:
            query:   string to test
            choices: list or dictionary of choices

        Returns: tuple with best match, score
    """
    return match_all(query, choices, match_func, strategy)[0]


def match_all(query, choices, match_func=None, strategy=MatchStrategy.SIMPLE_RATIO):
    """
        match scores from a list or dictionary given an input

        Arguments:
            query:   string to test
            choices: list or dictionary of choices

        Returns: list of tuples (match, score)
    """
    match_func = match_func or fuzzy_match
    if isinstance(choices, dict):
        _choices = list(choices.keys())
    elif isinstance(choices, list):
        _choices = choices
    else:
        raise ValueError('a list or dict of choices must be provided')
    matches = []
    for c in _choices:
        if isinstance(choices, dict):
            matches.append((choices[c], match_func(query, c, strategy)))
        else:
            matches.append((c, match_func(query, c, strategy)))

    # TODO solve ties

    return sorted(matches, key=lambda k: k[1], reverse=True)
