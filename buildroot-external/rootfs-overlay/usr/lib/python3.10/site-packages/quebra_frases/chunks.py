import re
import itertools
from quebra_frases.tokenization import word_tokenize
from quebra_frases.tokens import get_uncommon_tokens, get_common_tokens, get_exclusive_tokens
from quebra_frases.list_utils import flatten


def chunk(text, delimiters, strip=True):
    pattern = f"({'|'.join(list(delimiters))})"
    pts = re.split(pattern, text)
    if strip:
        return [p.strip() for p in pts if p.strip()]
    else:
        return pts


def chunk_list(some_list, delimiters):
    return [list(y) for x, y in itertools.groupby(
        some_list, lambda z: z in delimiters) if not x]


def get_common_chunks(samples, squash=True):
    toks = get_uncommon_tokens(samples)
    chunks = [chunk_list(word_tokenize(s), toks) for s in samples]
    chunks = [[" ".join(_) for _ in s] for s in chunks]
    if squash:
        return set(flatten(chunks))
    return chunks


def get_uncommon_chunks(samples, squash=True):
    toks = get_common_tokens(samples)
    chunks = [chunk_list(word_tokenize(s), toks) for s in samples]
    chunks = [[" ".join(_) for _ in s] for s in chunks]
    if squash:
        return set(flatten(chunks))
    return chunks


def get_exclusive_chunks(samples, squash=True):
    toks = list(get_common_tokens(samples)) + \
           list(get_uncommon_tokens(samples))
    toks = [t for t in toks if t not in get_exclusive_tokens(samples)]
    chunks = [chunk_list(word_tokenize(s), toks) for s in samples]
    chunks = [[" ".join(_) for _ in s] for s in chunks]
    if squash:
        return set(flatten(chunks))
    return chunks


def find_spans(text, samples):
    chunks = chunk(text, samples, strip=False)
    spans = []
    idx = 0
    for sequence in chunks:
        if sequence in samples:
            end = idx + len(sequence)
            spans.append((idx, end, sequence))
        idx += len(sequence)
    return spans


