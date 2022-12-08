from quebra_frases.list_utils import flatten
from quebra_frases.tokenization import word_tokenize


def get_common_tokens(samples, squash=True):
    common_toks = []
    for s in samples:
        tokens = word_tokenize(s)
        others = [v for v in samples if v != s]
        other_tokens = [word_tokenize(_) for _ in others]
        common_toks.append([t for t in tokens if
                            all(t in toks for toks in other_tokens)])
    if squash:
        return set(flatten(common_toks))
    return common_toks


def get_uncommon_tokens(samples, squash=True):
    uncommon_toks = []
    for s in samples:
        tokens = word_tokenize(s)
        others = [v for v in samples if v != s]
        other_tokens = [word_tokenize(_) for _ in others]
        uncommon_toks.append([t for t in tokens if
                              any(t not in toks for toks in other_tokens)])
    if squash:
        return set(flatten(uncommon_toks))
    return uncommon_toks


def get_exclusive_tokens(samples, squash=True):
    exclusives = []
    for s in samples:
        tokens = word_tokenize(s)
        others = [v for v in samples if v != s]
        other_tokens = flatten([word_tokenize(_) for _ in others])
        exclusives.append([t for t in tokens if t not in other_tokens])
    if squash:
        return set(flatten(exclusives))
    return exclusives
