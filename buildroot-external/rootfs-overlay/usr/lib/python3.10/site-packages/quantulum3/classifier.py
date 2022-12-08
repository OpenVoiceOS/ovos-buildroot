# -*- coding: utf-8 -*-
"""
:mod:`Quantulum` classifier functions.
"""

import json
import logging
import multiprocessing
import os

import pkg_resources

from . import language, load
from .load import cached

# Semi-dependencies
try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier

    USE_CLF = True
except ImportError:
    SGDClassifier, TfidfVectorizer = None, None
    USE_CLF = False

try:
    import wikipedia
except ImportError:
    wikipedia = None


_LOGGER = logging.getLogger(__name__)


@cached
def _get_classifier(lang="en_US"):
    return language.get("classifier", lang)


###############################################################################
def ambiguous_units(lang="en_US"):  # pragma: no cover
    """
    Determine ambiguous units
    :return: list ( tuple( key, list (Unit) ) )
    """
    ambiguous = [
        i for i in list(load.units(lang).surfaces_all.items()) if len(i[1]) > 1
    ]
    ambiguous += [i for i in list(load.units(lang).symbols.items()) if len(i[1]) > 1]
    ambiguous += [i for i in list(load.entities(lang).derived.items()) if len(i[1]) > 1]
    return ambiguous


###############################################################################
def download_wiki(store=True, lang="en_US"):  # pragma: no cover
    """
    Download WikiPedia pages of ambiguous units.
    @:param store (bool) store wikipedia data in wiki.json file
    """
    if not wikipedia:
        print("Cannot download wikipedia pages. Install package wikipedia first.")
        return

    wikipedia.set_lang(lang[:2])

    ambiguous = ambiguous_units()
    pages = set([(j.name, j.uri) for i in ambiguous for j in i[1]])

    print()
    objs = []
    for num, page in enumerate(pages):

        obj = {
            "_id": page[1],
            "url": "https://{}.wikipedia.org/wiki/{}".format(lang[:2], page[1]),
            "clean": page[1].replace("_", " "),
        }

        print("---> Downloading %s (%d of %d)" % (obj["clean"], num + 1, len(pages)))

        obj["text"] = wikipedia.page(obj["clean"], auto_suggest=False).content
        obj["unit"] = page[0]
        objs.append(obj)

    path = language.topdir(lang).joinpath("train/wiki.json")
    if store:
        with path.open("w") as wiki_file:
            json.dump(objs, wiki_file, indent=4, sort_keys=True)

    print("\n---> All done.\n")
    return objs


###############################################################################
def clean_text(text, lang="en_US"):
    """
    Clean text for TFIDF
    """
    return _get_classifier(lang).clean_text(text)


def _clean_text_lang(lang):
    return _get_classifier(lang).clean_text


###############################################################################
def train_classifier(
    parameters=None, ngram_range=(1, 1), store=True, lang="en_US", n_jobs=None
):

    """
    Train the intent classifier
    TODO auto invoke if sklearn version is new or first install or sth
    @:param store (bool) store classifier in clf.joblib
    """
    _LOGGER.info("Started training, parallelized with {} jobs".format(n_jobs))
    _LOGGER.info("Loading training set")
    training_set = load.training_set(lang)
    target_names = list(frozenset([i["unit"] for i in training_set]))

    _LOGGER.info("Preparing training set")

    if n_jobs is None:
        try:
            # Retreive the number of cpus that can be used
            n_jobs = len(os.sched_getaffinity(0))
        except AttributeError:
            # n_jobs stays None such that Pool will try to
            # automatically set the number of processes appropriately
            pass
    with multiprocessing.Pool(processes=n_jobs) as p:
        train_data = p.map(_clean_text_lang(lang), [ex["text"] for ex in training_set])

    train_target = [target_names.index(example["unit"]) for example in training_set]

    tfidf_model = TfidfVectorizer(
        sublinear_tf=True,
        ngram_range=ngram_range,
        stop_words=_get_classifier(lang).stop_words(),
    )

    _LOGGER.info("Fit TFIDF Model")
    matrix = tfidf_model.fit_transform(train_data)

    if parameters is None:
        parameters = {
            "loss": "log",
            "penalty": "l2",
            "tol": 1e-3,
            "n_jobs": n_jobs,
            "alpha": 0.0001,
            "fit_intercept": True,
            "random_state": 0,
        }

    _LOGGER.info("Fit SGD Classifier")
    clf = SGDClassifier(**parameters).fit(matrix, train_target)
    obj = {
        "scikit-learn_version": pkg_resources.get_distribution("scikit-learn").version,
        "tfidf_model": tfidf_model,
        "clf": clf,
        "target_names": target_names,
    }
    if store:  # pragma: no cover
        path = language.topdir(lang).joinpath("clf.joblib")
        _LOGGER.info("Store classifier at {}".format(path))
        with path.open("wb") as file:
            joblib.dump(obj, file)
    return obj


###############################################################################
class Classifier(object):
    def __init__(self, obj=None, lang="en_US"):
        """
        Load the intent classifier
        """
        self.tfidf_model = None
        self.classifier = None
        self.target_names = None

        if not USE_CLF:
            return

        if not obj:
            path = language.topdir(lang).joinpath("clf.joblib")
            with path.open("rb") as file:
                obj = joblib.load(file)

        cur_scipy_version = pkg_resources.get_distribution("scikit-learn").version
        if cur_scipy_version != obj.get("scikit-learn_version"):  # pragma: no cover
            _LOGGER.warning(
                "The classifier was built using a different scikit-learn "
                "version (={}, !={}). The disambiguation tool could behave "
                "unexpectedly. Consider running classifier.train_classfier()".format(
                    obj.get("scikit-learn_version"), cur_scipy_version
                )
            )

        self.tfidf_model = obj["tfidf_model"]
        self.classifier = obj["clf"]
        self.target_names = obj["target_names"]


@cached
def classifier(lang="en_US"):
    """
    Cached classifier object
    :param lang:
    :return:
    """
    return Classifier(lang=lang)


###############################################################################
def disambiguate_entity(key, text, lang="en_US"):
    """
    Resolve ambiguity between entities with same dimensionality.
    """

    new_ent = next(iter(load.entities(lang).derived[key]))
    if len(load.entities(lang).derived[key]) > 1:
        transformed = classifier(lang).tfidf_model.transform([clean_text(text, lang)])
        scores = classifier(lang).classifier.predict_proba(transformed).tolist()[0]
        scores = zip(scores, classifier(lang).target_names)

        # Filter for possible names
        names = [i.name for i in load.entities(lang).derived[key]]
        scores = [i for i in scores if i[1] in names]

        # Sort by rank
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        try:
            new_ent = load.entities(lang).names[scores[0][1]]
        except IndexError:
            _LOGGER.debug('\tAmbiguity not resolved for "%s"', str(key))

    return new_ent


###############################################################################
def disambiguate_unit(unit, text, lang="en_US"):
    """
    Resolve ambiguity between units with same names, symbols or abbreviations.
    """

    new_unit = (
        load.units(lang).symbols.get(unit)
        or load.units(lang).surfaces.get(unit)
        or load.units(lang).surfaces_lower.get(unit.lower())
        or load.units(lang).symbols_lower.get(unit.lower())
    )
    if not new_unit:
        return load.units(lang).names.get("unk")

    if len(new_unit) > 1:
        transformed = classifier(lang).tfidf_model.transform([clean_text(text, lang)])
        scores = classifier(lang).classifier.predict_proba(transformed).tolist()[0]
        scores = zip(scores, classifier(lang).target_names)

        # Filter for possible names
        names = [i.name for i in new_unit]
        scores = [i for i in scores if i[1] in names]

        # Sort by rank
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        try:
            final = load.units(lang).names[scores[0][1]]
            _LOGGER.debug('\tAmbiguity resolved for "%s" (%s)' % (unit, scores))
        except IndexError:
            _LOGGER.debug('\tAmbiguity not resolved for "%s"' % unit)
            final = next(iter(new_unit))
    else:
        final = next(iter(new_unit))

    return final
