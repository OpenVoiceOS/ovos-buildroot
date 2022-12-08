from phoneme_guesser.exceptions import CantGuessPhonemesForLang, FailedToGuessPhonemes
from phoneme_guesser.utils import normalize_word, match_one
from os.path import join, dirname

# lazy loading, when needed the first time dict will be kept in memory
_loaded_langs = {}


def load_phoneme_dict(lang):
    global _loaded_langs

    base = join(dirname(__file__), "res")
    if lang.startswith("en"):
        path = join(base, "en-us.dict")
    elif lang == "es-mx":
        path = join(base, "es-mx.dict")
    elif lang.startswith("es"):
        path = join(base, "es.dict")
    elif lang == "pt-br":
        path = join(base, "pt-br.dict")
    elif lang.startswith("fr"):
        path = join(base, "fr.dict")
    elif lang.startswith("it"):
        path = join(base, "it.dict")
    elif lang.startswith("nl"):
        path = join(base, "nl.dict")
    elif lang.startswith("de"):
        path = join(base, "de.dict")
    elif lang.startswith("ca"):
        path = join(base, "ca-es.dict")
    else:
        raise CantGuessPhonemesForLang("phoneme dict not available")

    # lazy load
    if path in _loaded_langs:
        return _loaded_langs[path]

    phones = {}
    with open(path) as f:
        lines = f.read().split("\n")
        for l in lines:
            word = l.split(" ")[0]
            pho = [p for p in l.split(" ")[1:] if p.strip()]
            phones[word] = pho

    _loaded_langs[path] = phones
    return phones


def _guess_phonemes_en(word):
    word = normalize_word(word)
    basic_pronunciations = {'a': ['AE'], 'b': ['B'], 'c': ['K'],
                            'd': ['D'],
                            'e': ['EH'], 'f': ['F'], 'g': ['G'],
                            'h': ['HH'],
                            'i': ['IH'],
                            'j': ['JH'], 'k': ['K'], 'l': ['L'],
                            'm': ['M'],
                            'n': ['N'], 'o': ['OW'], 'p': ['P'],
                            'qu': ['K', 'W'], 'r': ['R'],
                            's': ['S'], 't': ['T'], 'u': ['AH'],
                            'v': ['V'],
                            'w': ['W'], 'x': ['K', 'S'], 'y': ['Y'],
                            'z': ['Z'], 'ch': ['CH'],
                            'sh': ['SH'], 'th': ['TH'], 'dg': ['JH'],
                            'dge': ['JH'], 'psy': ['S', 'AY'],
                            'oi': ['OY'],
                            'ee': ['IY'],
                            'ao': ['AW'], 'ck': ['K'], 'tt': ['T'],
                            'nn': ['N'], 'ai': ['EY'], 'eu': ['Y', 'UW'],
                            'ue': ['UW'],
                            'ie': ['IY'], 'ei': ['IY'], 'ea': ['IY'],
                            'ght': ['T'], 'ph': ['F'], 'gn': ['N'],
                            'kn': ['N'], 'wh': ['W'],
                            'wr': ['R'], 'gg': ['G'], 'ff': ['F'],
                            'oo': ['UW'], 'ua': ['W', 'AO'], 'ng': ['NG'],
                            'bb': ['B'],
                            'tch': ['CH'], 'rr': ['R'], 'dd': ['D'],
                            'cc': ['K', 'S'], 'oe': ['OW'],
                            'igh': ['AY'], 'eigh': ['EY']}
    phones = []
    progress = len(word) - 1
    while progress >= 0:
        if word[0:3] in basic_pronunciations.keys():
            for phone in basic_pronunciations[word[0:3]]:
                phones.append(phone)
            word = word[3:]
            progress -= 3
        elif word[0:2] in basic_pronunciations.keys():
            for phone in basic_pronunciations[word[0:2]]:
                phones.append(phone)
            word = word[2:]
            progress -= 2
        elif word[0] in basic_pronunciations.keys():
            for phone in basic_pronunciations[word[0]]:
                phones.append(phone)
            word = word[1:]
            progress -= 1
        else:
            return None
    return phones


def _guess_phonemes_es(word):
    word = normalize_word(word)
    word = word.replace("h", "") \
        .replace("ci", "zi") \
        .replace("ce", "ze") \
        .replace("c", "k") \
        .replace("qu", "k") \
        .replace("sc", "z") \
        .replace("ge", "je") \
        .replace("gi", "ji") \
        .replace("ll", "#")
    phones = [c for c in word]
    for idx, pho in enumerate(phones):
        if pho == "#":
            phones[idx] = "ll"
    return phones


def guess_phonemes_from_dict(word, lang):
    phones = load_phoneme_dict(lang)
    if word in phones:
        return phones[word], 1
    return match_one(word, phones)


def guess_phonemes(word, lang):
    lang = lang.lower()
    if lang.startswith("en"):
        return _guess_phonemes_en(word)
    elif lang.startswith("es"):
        return _guess_phonemes_es(word)
    else:
        return guess_phonemes_from_dict(word, lang)[0]


def get_phonemes(phrase, lang):
    lang = lang.lower()
    phonemes = None
    if " " in phrase:
        total_phonemes = []
        words = phrase.split(" ")
        for phrase in words:
            phon = get_phonemes(phrase, lang)
            if phon is None:
                raise FailedToGuessPhonemes
            total_phonemes.extend(phon)
            total_phonemes.append(" . ")
        if total_phonemes[-1] == " . ":
            total_phonemes = total_phonemes[:-1]
        phonemes = "".join(total_phonemes)
    else:
        guess = guess_phonemes(phrase, lang)
        if guess is not None:
            phonemes = " ".join(guess)
    if phonemes is None:
        raise FailedToGuessPhonemes
    return phonemes

