#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` parser.
"""

import re
from importlib import import_module
from pathlib import Path

TOPDIR = Path(__file__).parent or Path(".")


###############################################################################
def languages():
    subdirs = [
        x
        for x in TOPDIR.joinpath("_lang").iterdir()
        if x.is_dir() and not x.name.startswith("__")
    ]
    langs = dict((x.name.lower(), x.name) for x in subdirs)
    langs.update((x.name[:2].lower(), x.name) for x in subdirs)
    return langs


# Not to be used directly, use subdir
_SUBDIRS = languages()
# Set of all supported languages
LANGUAGES = _SUBDIRS.keys()


def subdir(lang="en_US"):
    # convert to language string
    lang = re.sub(r"[\s\-]", "_", lang).lower()
    try:
        # search for correct submodule
        subdirs = _SUBDIRS[lang]
    except KeyError:
        raise NotImplementedError("Unsupported language: {}".format(lang))
    return subdirs


###############################################################################
def get(module, lang="en_US"):
    """
    Get module for given language
    :param module:
    :param lang:
    :return:
    """

    module = import_module(
        "._lang.{}.{}".format(subdir(lang), module), package=__package__
    )
    return module


###############################################################################
def topdir(lang="en_US"):
    return TOPDIR.joinpath("_lang", subdir(lang))
