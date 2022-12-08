# # NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# # All trademark and other rights reserved by their respective owners
# # Copyright 2008-2021 Neongecko.com Inc.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from datetime import timedelta

# TODO use padacioso and allow localization of "intents"
import simplematch
from requests_cache import CachedSession

from neon_solvers import AbstractSolver


class DDGSolver(AbstractSolver):
    def __init__(self):
        super(DDGSolver, self).__init__(name="DuckDuckGo", priority=75, config={"lang": "en"})
        self.session = CachedSession(backend="memory", expire_after=timedelta(minutes=5))

    def extract_keyword(self, query, lang="en"):
        query = query.lower()
        match = None

        # TODO localization
        if lang == "en":
            match = simplematch.match("who is {query}", query) or \
                    simplematch.match("what is {query}", query) or \
                    simplematch.match("when is {query}", query) or \
                    simplematch.match("tell me about {query}", query)

        if match:
            match = match["query"]
        else:
            return None

        words = match.split(" ")
        return " ".join([w for w in words if len(w) > 2])

    @staticmethod
    def match_infobox_field(query, lang="en"):
        if lang != "en":
            # TODO localization
            return None, None

        query = query.lower()

        # known for
        match = simplematch.match("what is {query} known for", query) or \
                simplematch.match("what is {query} famous for", query)
        if match:
            return match["query"], "known for"

        # resting place
        match = simplematch.match("where is {query} resting place*", query) or \
                simplematch.match("where is {query} resting buried*", query)
        if match:
            return match["query"], "resting place"

        # birthday
        match = simplematch.match("when was {query} born*", query) or \
                simplematch.match("when is {query} birth*", query)
        if match:
            return match["query"], "born"

        # death
        match = simplematch.match("when was {query} death*", query) or \
                simplematch.match("when did {query} die*", query) or \
                simplematch.match("what was {query} *death", query) or \
                simplematch.match("what is {query} *death", query)

        if match:
            return match["query"], "died"

        # children
        match = simplematch.match("how many children did {query} have*",
                                  query) or \
                simplematch.match("how many children does {query} have*",
                                  query)
        if match:
            return match["query"], "children"

        # alma mater
        match = simplematch.match("what is {query} alma mater", query) or \
                simplematch.match("where did {query} study*", query)
        if match:
            return match["query"], "alma mater"

        return None, None

    def get_infobox(self, query, context=None):
        data = self.extract_and_search(query, context)  # handles translation
        # parse infobox
        related_topics = [t.get("Text") for t in data.get("RelatedTopics", [])]
        infobox = {}
        infodict = data.get("Infobox") or {}
        for entry in infodict.get("content", []):
            k = entry["label"].lower().strip()
            infobox[k] = entry["value"]
        return infobox, related_topics

    def extract_and_search(self, query, context=None):
        """
        extract search term from query and perform search
        """
        query, context, lang = self._tx_query(query, context)

        # match the full query
        data = self.get_data(query, context)
        if data:
            return data

        # extract the best keyword with some regexes or fallback to RAKE
        kw = self.extract_keyword(query, lang)
        return self.get_data(kw, context)

    # officially exported Solver methods
    def get_data(self, query, context):
        """
        query assured to be in self.default_lang
        return a dict response
        """
        # duck duck go api request
        try:
            data = self.session.get("https://api.duckduckgo.com",
                                    params={"format": "json",
                                            "q": query}).json()
        except:
            return {}
        return data

    def get_image(self, query, context=None):
        """
        query assured to be in self.default_lang
        return path/url to a single image to acompany spoken_answer
        """
        data = self.extract_and_search(query, context)
        image = data.get("Image") or \
                "https://github.com/JarbasSkills/skill-ddg/raw/master/ui/logo.png"
        if image.startswith("/"):
            image = "https://duckduckgo.com" + image
        return image

    def get_spoken_answer(self, query, context=None):
        """
        query assured to be in self.default_lang
        return a single sentence text response
        """
        query, context, lang = self._tx_query(query, context)

        # match an infobox field with some basic regexes
        # (primitive intent parsing)
        selected, key = self.match_infobox_field(query, lang)

        if key:
            selected = self.extract_keyword(selected, lang)
            infobox = self.get_infobox(selected, context)[0] or {}
            answer = infobox.get(key)
            if answer:
                return answer

        # return summary
        data = self.extract_and_search(query, context)
        return data.get("AbstractText")

    def get_expanded_answer(self, query, context=None):
        """
        query assured to be in self.default_lang
        return a list of ordered steps to expand the answer, eg, "tell me more"

        {
            "title": "optional",
            "summary": "speak this",
            "img": "optional/path/or/url
        }
        :return:
        """
        data = self.get_data(query, context)
        img = self.get_image(query, context)
        steps = [{
            "title": query,
            "summary": s,
            "img": img
        } for s in self.sentence_split(data.get("AbstractText", ""), -1) if s]

        infobox, _ = self.get_infobox(query)
        steps += [{"title": k,
                   "summary": k + " - " + str(v),
                   "img": img} for k, v in infobox.items()
                  if not k.endswith(" id") and  # itunes id
                  not k.endswith(" profile") and  # twitter profile
                  k != "instance of"]  # spammy and sounds bad when spokem
        return steps


if __name__ == "__main__":
    from neon_solver_ddg_plugin import DDGSolver

    d = DDGSolver()

    query = "who is Isaac Newton"

    # full answer
    ans = d.spoken_answer(query)
    print(ans)
    # Sir Isaac Newton was an English mathematician, physicist, astronomer, alchemist, theologian, and author widely recognised as one of the greatest mathematicians and physicists of all time and among the most influential scientists. He was a key figure in the philosophical revolution known as the Enlightenment. His book Philosophiæ Naturalis Principia Mathematica, first published in 1687, established classical mechanics. Newton also made seminal contributions to optics, and shares credit with German mathematician Gottfried Wilhelm Leibniz for developing infinitesimal calculus. In the Principia, Newton formulated the laws of motion and universal gravitation that formed the dominant scientific viewpoint until it was superseded by the theory of relativity.

    # chunked answer, "tell me more"
    for sentence in d.long_answer(query):
        print(sentence["title"])
        print(sentence["summary"])
        print(sentence.get("img"))

        # who is Isaac Newton
        # Sir Isaac Newton was an English mathematician, physicist, astronomer, alchemist, theologian, and author widely recognised as one of the greatest mathematicians and physicists of all time and among the most influential scientists.
        # https://duckduckgo.com/i/ea7be744.jpg

        # who is Isaac Newton
        # He was a key figure in the philosophical revolution known as the Enlightenment.
        # https://duckduckgo.com/i/ea7be744.jpg

        # who is Isaac Newton
        # His book Philosophiæ Naturalis Principia Mathematica, first published in 1687, established classical mechanics.
        # https://duckduckgo.com/i/ea7be744.jpg

        # who is Isaac Newton
        # Newton also made seminal contributions to optics, and shares credit with German mathematician Gottfried Wilhelm Leibniz for developing infinitesimal calculus.
        # https://duckduckgo.com/i/ea7be744.jpg

        # who is Isaac Newton
        # In the Principia, Newton formulated the laws of motion and universal gravitation that formed the dominant scientific viewpoint until it was superseded by the theory of relativity.
        # https://duckduckgo.com/i/ea7be744.jpg

    # bidirectional auto translate by passing lang context
    sentence = d.spoken_answer("Quem é Isaac Newton",
                               context={"lang": "pt"})
    print(sentence)
    # Sir Isaac Newton foi um matemático inglês, físico, astrônomo, alquimista, teólogo e autor amplamente reconhecido como um dos maiores matemáticos e físicos de todos os tempos e entre os cientistas mais influentes. Ele era uma figura chave na revolução filosófica conhecida como o Iluminismo. Seu livro Philosophiæ Naturalis Principia Mathematica, publicado pela primeira vez em 1687, estabeleceu a mecânica clássica. Newton também fez contribuições seminais para a óptica, e compartilha crédito com o matemático alemão Gottfried Wilhelm Leibniz para desenvolver cálculo infinitesimal. No Principia, Newton formulou as leis do movimento e da gravitação universal que formaram o ponto de vista científico dominante até ser superado pela teoria da relatividade
