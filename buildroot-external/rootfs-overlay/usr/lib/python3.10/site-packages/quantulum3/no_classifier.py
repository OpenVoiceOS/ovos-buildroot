# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` disambiguation functions when no classifier is available
"""
from __future__ import division

from . import load


def disambiguate_no_classifier(entities, text, lang="en_US"):
    """
    Disambiguate the entity or unit without a classifier
    :param entities:
    :param text:
    :param lang:
    :return: a single entity or unit that has been chosen for
    """
    word_sets = load.training_set(lang)

    max_entity, max_count, max_relative = None, 0, 0
    for entity in entities:
        count = 0
        total = 0
        for word_set in word_sets:
            if word_set["unit"] == entity.name:
                total += len(word_set["text"])
                for word in word_set["text"].split(" "):
                    count += 1 if word in text else 0
        try:
            relative = count / total
        except ZeroDivisionError:
            relative = 0
        if relative > max_relative or (relative == max_relative and count > max_count):
            max_entity, max_count, max_relative = entity, count, relative
    return max_entity
