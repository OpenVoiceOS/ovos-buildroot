from difflib import SequenceMatcher
import re
from enum import IntEnum, auto
from ovos_utils.log import LOG

try:
    import rapidfuzz
except ImportError:
    rapidfuzz = None


class MatchStrategy(IntEnum):
    SIMPLE_RATIO = auto()
    RATIO = auto()
    PARTIAL_RATIO = auto()
    TOKEN_SORT_RATIO = auto()
    TOKEN_SET_RATIO = auto()
    PARTIAL_TOKEN_RATIO = auto()
    PARTIAL_TOKEN_SORT_RATIO = auto()
    PARTIAL_TOKEN_SET_RATIO = auto()


def _validate_matching_strategy(strategy):
    if rapidfuzz is None and strategy != MatchStrategy.SIMPLE_RATIO:
        LOG.error("rapidfuzz is not installed, "
                  "falling back to SequenceMatcher for all match strategies")
        LOG.warning("pip install rapidfuzz")
        return MatchStrategy.SIMPLE_RATIO
    return strategy


def fuzzy_match(x, against, strategy=MatchStrategy.SIMPLE_RATIO):
    """Perform a 'fuzzy' comparison between two strings.
    Returns:
        float: match percentage -- 1.0 for perfect match,
               down to 0.0 for no match at all.
    """
    strategy = _validate_matching_strategy(strategy)
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
    strategy = _validate_matching_strategy(strategy)
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


def remove_parentheses(answer):
    # remove [xx] (xx) {xx}
    answer = re.sub(r'\[[^)]*\]', '', answer)
    answer = re.sub(r'\([^)]*\)', '', answer)
    answer = re.sub(r'\{[^)]*\}', '', answer)
    answer = answer.replace("(", "").replace(")", "") \
        .replace("[", "").replace("]", "").replace("{", "") \
        .replace("}", "").strip()
    # remove extra spaces
    words = [w for w in answer.split(" ") if w.strip()]
    answer = " ".join(words)
    if not answer:
        return None
    return answer

