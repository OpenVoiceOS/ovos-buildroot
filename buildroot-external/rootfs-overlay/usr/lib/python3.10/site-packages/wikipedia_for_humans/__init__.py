import wikipediaapi
import requests
from wikipedia_for_humans.util import match_one, fuzzy_match, \
    split_sentences, summarize, remove_parentheses, singularize
from wikipedia_for_humans.exceptions import DisambiguationError
from quebra_frases import word_tokenize, sentence_tokenize


# internal handling of wikipediaapi
def _get_page(page_name, lang="en", strict=False, auto_disambiguate=False):
    if isinstance(page_name, wikipediaapi.WikipediaPage):
        return page_name
    wiki_wiki = wikipediaapi.Wikipedia(lang)
    page_py = wiki_wiki.page(page_name)
    cats = get_categories(page_py)
    if "Disambiguation pages" in cats:
        if strict:
            raise DisambiguationError
        if auto_disambiguate:
            page_name, score = disambiguate(page_name, lang)
            page_py = _get_page(page_name, lang, strict)
    return page_py


def _get_summary(page_name, lang="en"):
    if isinstance(page_name, str):
        page = _get_page(page_name, lang)
    else:
        # TODO confirm page is page object
        page = page_name
    return page.summary


def _get_title(page_name, lang="en"):
    if isinstance(page_name, str):
        page = _get_page(page_name, lang)
    else:
        # TODO confirm page is page object
        page = page_name
    return page.title


def _get_text(page_name, lang="en"):
    if isinstance(page_name, str):
        page = _get_page(page_name, lang)
    else:
        # TODO confirm page is page object
        page = page_name
    return page.text


def _get_images(page_name, lang="en"):
    if isinstance(page_name, str):
        page = _get_page(page_name, lang)
    else:
        # TODO confirm page is page object
        page = page_name
    url = "http://en.wikipedia.org/w/api.php"
    params = {"action": "query",
              "titles": page.title,
              "prop": "pageimages",
              "piprop": "original",
              "format": "json"}
    return requests.get(url, params=params).json()["query"]["pages"]


def _get_wikiroulette(lang="en"):
    url = f"https://{lang}.wikipedia.org/wiki/Special:Random"
    article_url = requests.get(url).url
    article = article_url.replace(f"https://{lang}.wikipedia.org/wiki/", "")
    return _get_page(article, lang)


# parsing functions
def get_sections(page_name, lang="en"):
    if isinstance(page_name, str):
        page = _get_page(page_name, lang)
    else:
        # TODO confirm page is page object
        page = page_name
    if page is None:
        return None

    n = {}

    def parse_sections(sections, level=0):
        for s in sections:
            parse_sections(s.sections, level + 1)
            n[s.title] = s.text

    parse_sections(page.sections)
    return n


def get_categories(page_name, lang="en"):
    if isinstance(page_name, str):
        page = _get_page(page_name, lang)
    else:
        # TODO confirm page is page object
        page = page_name
    if page is None:
        return None
    return [cat.replace("Category:", "") for cat in page.categories]


def get_page(page_name, lang="en", strict=False):
    page = _get_page(page_name, lang, strict)
    if page.exists():
        return {"title": _get_title(page),
                "summary": _get_summary(page),
                "categories": get_categories(page),
                "sections": get_sections(page),
                "text": _get_text(page)}
    return None


def search_wikipedia(query, limit=3):
    params = {"search": query,
              "format": "json",
              "namespace": 0,
              "limit": limit,
              "formatversion": 2,
              "action": "opensearch"}
    r = requests.get("https://en.wikipedia.org/w/api.php", params=params)
    _, results, _, urls = r.json()
    if len(results) == 0:
        return None
    return {"pages": results, "urls": urls}


def search_pages(query, limit=3):
    result = search_wikipedia(query, limit)
    if result is None:
        return None
    return result["pages"]


def search_urls(query, limit=3):
    result = search_wikipedia(query, limit)
    if result is None:
        return None
    return result["urls"]


def search_in_page(query, page_name, lang="en", all_matches=False,
                   thresh=0.1, paragraphs=True):
    sections = get_sections(page_name, lang)
    if isinstance(page_name, wikipediaapi.WikipediaPage):
        page_name = page_name.title
    page_name = singularize(remove_parentheses(page_name), lang).lower().strip()
    original_query = query
    query = singularize(remove_parentheses(query), lang).lower().strip()

    # search text inside sections
    candidates = []
    for sec in sections:
        # total half assed scoring metric #0
        # if query is a section title boost score
        base_score = 0
        if page_name in sec.lower():
            base_score += 10
        if original_query.lower() in sec.lower():
            base_score += 20
        if query in sec.lower():
            base_score += 15
        if query in singularize(sec.lower()):
            base_score += 10

        for c in split_sentences(sections[sec], paragraphs):
            if len(c.split(" ")) > 3:
                candidates.append((c, base_score))

    if not candidates:
        return [] if all_matches else None

    for idx, (c, score) in enumerate(candidates):
        tokens = [t.lower() for t in word_tokenize(c)]
        for word in tokens:
            # total half assed scoring metric #1
            # each time query appears in sentence/paragraph boost score
            if len(word) < 3:
                continue

            singular_word = singularize(word, lang)

            if query == word:
                # magic numbers are bad
                score += 40
            if query == singular_word:
                # magic numbers are bad
                score += 30
            # partial match
            if query in word or word in query:
                # magic numbers are bad
                score += 15
            if query in singular_word or singular_word in query:
                # magic numbers are bad
                score += 10

            # total half assed scoring metric #2
            # each time page name appears in sentence/paragraph boost score
            if word in page_name:
                # magic numbers are bad
                score += 5

        candidates[idx] = (c, score)

    # total half assed scoring metric #3
    # give preference to short sentences
    if not paragraphs:
        for idx, (c, score) in enumerate(candidates):
            score = score / len(c)
            candidates[idx] = (c, score)
    else:
        for idx, (c, score) in enumerate(candidates):
            score = score / len(split_sentences(c))
            candidates[idx] = (c, score)

    # normalize scores
    best_score = max(s for _, s in candidates) + 0.1
    # score of 1 always looks suspicious, so yeah, + 0.1 is cheating
    candidates = [(c, s/best_score) for c, s in candidates
                  if s/best_score >= thresh]
    candidates.sort(key=lambda k: k[1], reverse=True)
    if all_matches:
        return candidates
    return candidates[0]


def search_paragraphs(query, page_name, lang="en", thresh=0.15):
    return search_in_page(query, page_name, lang, thresh=thresh,
                          all_matches=True, paragraphs=True)


def search_sentences(query, page_name, lang="en", thresh=0.2):
    return search_in_page(query, page_name, lang, thresh=thresh,
                          all_matches=True, paragraphs=False)


def disambiguate(page_name, context="", all_matches=False, lang="en"):
    try:
        page = get_page(page_name, lang, strict=True)
        if not page:
            raise ValueError
        if all_matches:
            return [(page["title"], 1)]
        return page["title"], 1
    except DisambiguationError:
        page = get_page(page_name, lang)
    except:
        results = search_wikipedia(page_name, limit=1)
        if results is None:
            if all_matches:
                return []
            return None, 0
        return disambiguate(results["pages"][0])
    page_name = page["title"].strip()
    top_ambiguous = page["summary"]
    top_ambiguous = top_ambiguous.replace(
        "{p} usually refers to:".format(p=page_name), "")
    top_ambiguous = top_ambiguous.replace(
        "{p} may also refer to:".format(p=page_name), "")
    top_ambiguous = [p.strip() for p in top_ambiguous.split("\n") if p.strip()]

    if not context:
        if all_matches:
            return [(t, 0.5) for t in top_ambiguous]
        best = top_ambiguous[0].split(",")[0].strip()
        return best, 0.5

    sections = page["sections"]
    for s in sections:
        sections[s] = sections[s].split("\n")
    sections["most used"] = top_ambiguous
    scores = []
    candidates = []

    for sec in sections:
        base_score = 0
        # half assed metric #0
        # boost score of "usual" meanings
        if sec == "most used":
            base_score = 0.2

        # half assed metric #1
        # boost score if its in sections
        base_score += fuzzy_match(sec, context)

        # half assed metric #2
        # boost score per word count in sections text
        for c in sections[sec]:
            count = 0
            for word in c.split(" "):
                if context.rstrip("s") in word:
                    count += 1
                    # boost score if it's in first sentence of this passage
                    short = split_sentences(c)[0].split(",")[0]
                    if word.rstrip("s") in short:
                        count += 1
                    # boost score if passage is of the format Name (query)
                    if len(short.split(" ")) == 2 and context.rstrip("s") in \
                            short.split(" ")[1]:
                        count += 2
                # boost score of "usual" meanings
                if sec == "most used":
                    count += fuzzy_match(word, context) * 0.2
            candidates.append(c)
            scores.append(base_score + count * 0.2)

    best_score = max(scores)
    best_page_idx = scores.index(best_score)
    best = candidates[best_page_idx].split(",")[0].strip()

    # fake percent
    if best_score > 1:
        dif = best_score - 1
        scores = [s - dif for s in scores]
        scores = [s if s > 0 else 0.0001 for s in scores]
        best_score = 1

    if all_matches:

        matches = []
        for idx, c in enumerate(candidates):
            c = c.split(",")[0]
            if not c.strip():
                continue
            matches.append((c, scores[idx]))
        # TODO sorted
        matches.sort(key=lambda k: k[1], reverse=True)
        return matches

    return best, best_score


# Human functions
def summary(query, lang="en"):
    if isinstance(query, wikipediaapi.WikipediaPage):
        page = query
    else:
        results = search_wikipedia(query, limit=1)
        if results is None:
            return ""
        page = _get_page(results["pages"][0], lang, auto_disambiguate=True)

    answer = _get_summary(page, lang)
    return answer


def short_answer(query, lang="en"):
    answer = summary(query, lang)
    if not answer:
        return None
    return summarize(answer)


def ask_about(query, page_name, lang="en"):
    if isinstance(page_name, wikipediaapi.WikipediaPage):
        page = page_name
    else:
        results = search_wikipedia(page_name, limit=1)
        if results is None:
            return ""
        page = _get_page(results["pages"][0], lang, auto_disambiguate=True)

    answer, conf = search_in_page(query, page, lang, all_matches=False)
    return remove_parentheses(answer)


def tldr_about(query, page_name, lang="en"):
    if isinstance(page_name, wikipediaapi.WikipediaPage):
        page = page_name
    else:
        results = search_wikipedia(page_name, limit=1)
        if results is None:
            return ""
        page = _get_page(results["pages"][0], lang, auto_disambiguate=True)
    answer, conf = search_in_page(query, page, lang, all_matches=False,
                                  paragraphs=False)
    return summarize(answer)


def long_answer(query, lang="en"):
    return summary(query, lang=lang)


def short_summary(query, lang="en"):
    return short_answer(query, lang)


def tldr(query, lang="en"):
    return short_answer(query, lang)


def best_sentence(query, page_name, lang="en"):
    return tldr_about(query, page_name, lang=lang)


def best_paragraph(query, page_name, lang="en"):
    return ask_about(query, page_name, lang=lang)


def page_data(query, lang="en"):
    if isinstance(query, wikipediaapi.WikipediaPage):
        page = query
    else:
        results = search_wikipedia(query, limit=1)
        if results is None:
            return ""
        page = _get_page(results["pages"][0], lang, auto_disambiguate=True)
    sections_to_skip = ['External links', 'Further reading',
                        'Notes and references', 'See also']
    try:
        return {
            "categories": [k.split("Category:")[-1] for k in page._categories],
            "title": page.title,
            "page_id": page.pageid,
            "lang": page.language,
            "summary": page.summary,
            "url": page.fullurl,
            "images": images(page, lang),
            "sections": [{
                "title": s.title,
                "text": s.text
            } for s in page.sections if s.text and s.title not in sections_to_skip]
        }
    except KeyError:
        # some pages fail to parse
        return {}


def images(query, lang="en"):
    if isinstance(query, wikipediaapi.WikipediaPage):
        page = query
    else:
        results = search_wikipedia(query, limit=1)
        if results is None:
            return ""
        page = _get_page(results["pages"][0], lang, auto_disambiguate=True)
    return [p["original"]["source"] for k, p in _get_images(page, lang).items()
            if "original" in p]


def wikiroulette(lang="en"):
    data = {}
    while not data.get("url"):  # upstream may fail to parse and return title only
        data = page_data(_get_wikiroulette(lang), lang)
    return data

