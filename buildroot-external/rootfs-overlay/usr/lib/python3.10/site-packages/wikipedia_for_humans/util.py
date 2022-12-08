from difflib import SequenceMatcher
import re
from inflection import singularize as _singularize_en
from quebra_frases import sentence_tokenize, flatten


def singularize(word, lang="en"):
    if lang.startswith("en"):
        return _singularize_en(word)
    return word.rstrip("s")


def split_sentences(text, new_lines=False):
    if new_lines:
        return text.split("\n")
    return flatten([sentence_tokenize(t) for t in text.split("\n")])


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


def summarize(answer):
    if not answer:
        return None
    return normalize(split_sentences(answer)[0])


def normalize(answer):
    if not answer:
        return None
    return remove_parentheses(answer)


if __name__ == "__main__":
    s = "hello. He said"
    for s in split_sentences(s):
        print(s)
    s = "hello . He said"
    for s in split_sentences(s):
        print(s)

    # no splitting
    s = "hello.com"
    for s in split_sentences(s):
        print(s)
    s = "A.E:I.O.U"
    for s in split_sentences(s):
        print(s)

    # ambiguous, but will split
    s = "hello.He said"
    for s in split_sentences(s):
        print(s)

    # ambiguous, no split
    s = "hello. he said"  # could be "Jones Jr. thinks ..."
    for s in split_sentences(s):
        print(s)
    s = "hello.he said"  # could be  "www.hello.com"
    for s in split_sentences(s):
        print(s)
    s = "hello . he said"  # TODO maybe split this one?
    for s in split_sentences(s):
        print(s)
