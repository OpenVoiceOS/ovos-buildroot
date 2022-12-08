from mycroft_bus_client.message import dig_for_message


class PosTagger:
    def __init__(self, config=None):
        self.config = config or {}

    @property
    def lang(self):
        lang = self.config.get("lang")
        msg = dig_for_message()
        if msg:
            lang = msg.data.get("lang")
        return lang or "en-us"

    def postag(self, spans, lang=None):
        lang = lang or self.lang
        # this should be implemented by plugins!
        if lang.startswith("pt"):
            return _dummy_postag_pt(spans)
        elif lang.startswith("en"):
            return _dummy_postag_en(spans)
        return _dummy_postag(spans)


def _dummy_postag_pt(spans):
    pos = []
    for s, e, t in spans:
        if t == "e":
            pos.append((s, e, t, "CONJ"))
        elif t in ["o", "a", "os", "as"]:
            pos.append((s, e, t, "DET"))
        elif t.lower() in ["ele", "ela", "eles", "elas", "nós", "vós"]:
            pos.append((s, e, t, "PRON"))
        elif t in ["do", "da", "dos", "das"]:
            pos.append((s, e, t, "ADP"))
        elif t.isdigit():
            pos.append((s, e, t, "NUMBER"))
        elif t[0].isupper() and len(t) >= 5:
            pos.append((s, e, t, "PROPN"))
        elif len(t) >= 4:
            pos.append((s, e, t, "NOUN"))
        else:
            pos.append((s, e, t, "VERB"))
    return pos


def _dummy_postag_en(spans):
    pos = []
    for s, e, t in spans:
        if t == "and":
            pos.append((s, e, t, "CONJ"))
        elif t in ["the", "a", "an"]:
            pos.append((s, e, t, "DET"))
        elif t.lower() in ["he", "she", "it", "they"]:
            pos.append((s, e, t, "PRON"))
        elif t in ["of", "for"]:
            pos.append((s, e, t, "ADP"))
        elif t.isdigit():
            pos.append((s, e, t, "NUMBER"))
        elif t[0].isupper() and len(t) >= 5:
            pos.append((s, e, t, "PROPN"))
        elif len(t) >= 4:
            pos.append((s, e, t, "NOUN"))
        else:
            pos.append((s, e, t, "VERB"))
    return pos


def _dummy_postag(spans):
    pos = []
    for s, e, t in spans:
        if t.isdigit():
            pos.append((s, e, t, "NUMBER"))
        elif t[0].isupper() and len(t) >= 4:
            pos.append((s, e, t, "PROPN"))
        elif len(t) >= 5:
            pos.append((s, e, t, "NOUN"))
        else:
            pos.append((s, e, t, "VERB"))
    return pos
