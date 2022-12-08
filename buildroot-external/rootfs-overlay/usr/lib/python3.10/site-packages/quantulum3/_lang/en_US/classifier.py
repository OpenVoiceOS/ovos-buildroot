# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classifier functions.
"""

import re
import string

try:
    from stemming.porter2 import stem
except ImportError:
    stem = None

_WORD_DIV = re.compile(r"[%s]" % re.escape(string.punctuation))
_NUMBERS = re.compile(r"[0-9]")


###############################################################################
def clean_text(text):
    """
    Clean text for TFIDF
    """
    if not stem:
        raise ImportError("Module stemming is not installed.")

    new_text = _WORD_DIV.sub(" ", text.lower())

    new_text = [stem(i) for i in new_text.split() if not _NUMBERS.search(i)]

    new_text = " ".join(new_text)

    return new_text


###############################################################################
def stop_words():
    """
    Return the string, identifying stop word language for TFIDF vectorizer
    :return:
    """
    return "english"
