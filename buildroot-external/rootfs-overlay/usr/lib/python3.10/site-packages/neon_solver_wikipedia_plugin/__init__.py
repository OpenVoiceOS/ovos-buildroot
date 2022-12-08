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
import simplematch
import wikipedia_for_humans
from neon_solvers import AbstractSolver


class WikipediaSolver(AbstractSolver):
    def __init__(self, config=None):
        super(WikipediaSolver, self).__init__(name="Wikipedia", config=config)
        self.cache.clear()

    def extract_keyword(self, query, lang="en"):
        query = query.lower()

        # regex from narrow to broader matches
        match = None
        if lang == "en":
            match = simplematch.match("who is {query}", query) or \
                    simplematch.match("what is {query}", query) or \
                    simplematch.match("when is {query}", query) or \
                    simplematch.match("tell me about {query}", query)
        # TODO localization
        if match:
            match = match["query"]
        else:
            return None
        return match

    def get_secondary_search(self, query, lang="en"):
        if lang == "en":
            match = simplematch.match("what is the {subquery} of {query}", query)
            if match:
                return match["query"], match["subquery"]
        query = self.extract_keyword(query, lang)
        return query, None

    def extract_and_search(self, query, context=None):
        context = context or {}
        lang = context.get("lang") or self.default_lang
        lang = lang.split("-")[0]

        # extract the best keyword with some regexes or fallback to RAKE
        query = self.extract_keyword(query, lang)
        if not query:
            return {}
        return self.search(query, context)

    # officially exported Solver methods
    def get_data(self, query, context=None):
        """
       query assured to be in self.default_lang
       return a dict response
       """
        context = context or {}
        lang = context.get("lang") or self.default_lang
        lang = lang.split("-")[0]

        page_data = wikipedia_for_humans.page_data(query, lang=lang) or {}
        data = {
            "short_answer": wikipedia_for_humans.tldr(query, lang=lang),
            "summary": wikipedia_for_humans.summary(query, lang=lang)
        }
        if not page_data:
            query, subquery = self.get_secondary_search(query, lang)
            if subquery:
                data = {
                    "short_answer": wikipedia_for_humans.tldr_about(subquery, query, lang=lang),
                    "summary": wikipedia_for_humans.ask_about(subquery, query, lang=lang)
                }
            else:
                data = {
                    "short_answer": wikipedia_for_humans.tldr(query, lang=lang),
                    "summary": wikipedia_for_humans.summary(query, lang=lang)
                }
        page_data.update(data)
        page_data["title"] = page_data.get("title") or query
        return page_data

    def get_spoken_answer(self, query, context=None):
        data = self.extract_and_search(query, context)
        return  data.get("summary", "")

    def get_image(self, query, context=None):
        """
        query assured to be in self.default_lang
        return path/url to a single image to acompany spoken_answer
        """
        data = self.extract_and_search(query, context)
        try:
            return data["images"][0]
        except:
            return None

    def get_expanded_answer(self, query, context=None):
        """
        query assured to be in self.default_lang
        return a list of ordered steps to expand the answer, eg, "tell me more"

        {
            "title": "optional",
            "summary": "speak this",
            "img": "optional/path/or/url
        }

        """
        data = self.get_data(query, context)
        img = self.get_image(query, context)
        steps = [{
                "title": data.get("title", query).title(),
                "summary": s,
                "img": img
            }
            for s in self.sentence_split(data["summary"], -1)]
        for sec in data.get("sections", []):
            steps += [{
                "title": sec.get("title", query).title(),
                "summary": s,
                "img": img
            }
            for s in self.sentence_split(sec["text"], -1)]
        return steps


if __name__ == "__main__":
    d = WikipediaSolver()

    query = "who is Isaac Newton"

    # full answer
    ans = d.spoken_answer(query)
    print(ans)
    # Sir Isaac Newton  (25 December 1642 – 20 March 1726/27) was an English mathematician, physicist, astronomer, alchemist, theologian, and author (described in his time as a "natural philosopher") widely recognised as one of the greatest mathematicians and physicists of all time and among the most influential scientists. He was a key figure in the philosophical revolution known as the Enlightenment. His book Philosophiæ Naturalis Principia Mathematica (Mathematical Principles of Natural Philosophy), first published in 1687, established classical mechanics. Newton also made seminal contributions to optics, and shares credit with German mathematician Gottfried Wilhelm Leibniz for developing infinitesimal calculus.
    # In the Principia, Newton formulated the laws of motion and universal gravitation that formed the dominant scientific viewpoint until it was superseded by the theory of relativity. Newton used his mathematical description of gravity to derive Kepler's laws of planetary motion, account for tides, the trajectories of comets, the precession of the equinoxes and other phenomena, eradicating doubt about the Solar System's heliocentricity. He demonstrated that the motion of objects on Earth and celestial bodies could be accounted for by the same principles. Newton's inference that the Earth is an oblate spheroid was later confirmed by the geodetic measurements of Maupertuis, La Condamine, and others, convincing most European scientists of the superiority of Newtonian mechanics over earlier systems.
    # Newton built the first practical reflecting telescope and developed a sophisticated theory of colour based on the observation that a prism separates white light into the colours of the visible spectrum. His work on light was collected in his highly influential book Opticks, published in 1704. He also formulated an empirical law of cooling, made the first theoretical calculation of the speed of sound, and introduced the notion of a Newtonian fluid. In addition to his work on calculus, as a mathematician Newton contributed to the study of power series, generalised the binomial theorem to non-integer exponents, developed a method for approximating the roots of a function, and classified most of the cubic plane curves.
    # Newton was a fellow of Trinity College and the second Lucasian Professor of Mathematics at the University of Cambridge. He was a devout but unorthodox Christian who privately rejected the doctrine of the Trinity. He refused to take holy orders in the Church of England unlike most members of the Cambridge faculty of the day. Beyond his work on the mathematical sciences, Newton dedicated much of his time to the study of alchemy and biblical chronology, but most of his work in those areas remained unpublished until long after his death. Politically and personally tied to the Whig party, Newton served two brief terms as Member of Parliament for the University of Cambridge, in 1689–1690 and 1701–1702. He was knighted by Queen Anne in 1705 and spent the last three decades of his life in London, serving as Warden (1696–1699) and Master (1699–1727) of the Royal Mint, as well as president of the Royal Society (1703–1727).

    # chunked answer, "tell me more"
    for sentence in d.long_answer(query):
        print(sentence["title"])
        print(sentence["summary"])
        print(sentence.get("img"))

        # who is Isaac Newton
        # Sir Isaac Newton  (25 December 1642 – 20 March 1726/27) was an English mathematician, physicist, astronomer, alchemist, theologian, and author (described in his time as a "natural philosopher") widely recognised as one of the greatest mathematicians and physicists of all time and among the most influential scientists.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # He was a key figure in the philosophical revolution known as the Enlightenment.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # His book Philosophiæ Naturalis Principia Mathematica (Mathematical Principles of Natural Philosophy), first published in 1687, established classical mechanics.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # Newton also made seminal contributions to optics, and shares credit with German mathematician Gottfried Wilhelm Leibniz for developing infinitesimal calculus.
        # In the Principia, Newton formulated the laws of motion and universal gravitation that formed the dominant scientific viewpoint until it was superseded by the theory of relativity.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # Newton used his mathematical description of gravity to derive Kepler's laws of planetary motion, account for tides, the trajectories of comets, the precession of the equinoxes and other phenomena, eradicating doubt about the Solar System's heliocentricity.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # He demonstrated that the motion of objects on Earth and celestial bodies could be accounted for by the same principles.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # Newton's inference that the Earth is an oblate spheroid was later confirmed by the geodetic measurements of Maupertuis, La Condamine, and others, convincing most European scientists of the superiority of Newtonian mechanics over earlier systems.
        # Newton built the first practical reflecting telescope and developed a sophisticated theory of colour based on the observation that a prism separates white light into the colours of the visible spectrum.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # His work on light was collected in his highly influential book Opticks, published in 1704.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # He also formulated an empirical law of cooling, made the first theoretical calculation of the speed of sound, and introduced the notion of a Newtonian fluid.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # In addition to his work on calculus, as a mathematician Newton contributed to the study of power series, generalised the binomial theorem to non-integer exponents, developed a method for approximating the roots of a function, and classified most of the cubic plane curves.
        # Newton was a fellow of Trinity College and the second Lucasian Professor of Mathematics at the University of Cambridge.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # He was a devout but unorthodox Christian who privately rejected the doctrine of the Trinity.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # He refused to take holy orders in the Church of England unlike most members of the Cambridge faculty of the day.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # Beyond his work on the mathematical sciences, Newton dedicated much of his time to the study of alchemy and biblical chronology, but most of his work in those areas remained unpublished until long after his death.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

        # who is Isaac Newton
        # Politically and personally tied to the Whig party, Newton served two brief terms as Member of Parliament for the University of Cambridge, in 1689–1690 and 1701–1702.
        # https://upload.wikimedia.org/wikipedia/commons/3/3b/Portrait_of_Sir_Isaac_Newton%2C_1689.jpg

    # bidirectional auto translate by passing lang context
    sentence = d.spoken_answer("Quem é Isaac Newton",
                               context={"lang": "pt"})
    print(sentence)
    # Sir Isaac Newton (25 de dezembro de 1642 - 20 de março de 1726/27) foi um matemático, físico, astrônomo, alquimista, teólogo e autor (descrito em seu tempo como um "filósofo natural") amplamente reconhecido como um dos maiores matemáticos e físicos de todos os tempos e entre os cientistas mais influentes. Ele era uma figura chave na revolução filosófica conhecida como Iluminismo. Seu livro Philosophiæ Naturalis Principia Mathematica (Princípios matemáticos da Filosofia Natural), publicado pela primeira vez em 1687, estabeleceu a mecânica clássica. Newton também fez contribuições seminais para a óptica, e compartilha crédito com o matemático alemão Gottfried Wilhelm Leibniz para desenvolver cálculo infinitesimal.
    # No Principia, Newton formulou as leis do movimento e da gravitação universal que formaram o ponto de vista científico dominante até ser superado pela teoria da relatividade. Newton usou sua descrição matemática da gravidade para derivar as leis de Kepler do movimento planetário, conta para as marés, as trajetórias dos cometas, a precessão dos equinócios e outros fenômenos, erradicando dúvidas sobre a heliocentricidade do Sistema Solar. Ele demonstrou que o movimento de objetos na Terra e corpos celestes poderia ser contabilizado pelos mesmos princípios. A inferência de Newton de que a Terra é um esferóide oblate foi mais tarde confirmada pelas medidas geodésicas de Maupertuis, La Condamine, e outros, convencendo a maioria dos cientistas europeus da superioridade da mecânica newtoniana sobre sistemas anteriores.
    # Newton construiu o primeiro telescópio reflexivo prático e desenvolveu uma teoria sofisticada da cor baseada na observação de que um prisma separa a luz branca nas cores do espectro visível. Seu trabalho sobre luz foi coletado em seu livro altamente influente Opticks, publicado em 1704. Ele também formulou uma lei empírica de resfriamento, fez o primeiro cálculo teórico da velocidade do som e introduziu a noção de um fluido Newtoniano. Além de seu trabalho em cálculo, como um matemático Newton contribuiu para o estudo da série de energia, generalizou o teorema binomial para expoentes não inteiros, desenvolveu um método para aproximar as raízes de uma função e classificou a maioria das curvas de plano cúbico.
    # Newton era um companheiro do Trinity College e o segundo professor Lucasian de Matemática na Universidade de Cambridge. Ele era um cristão devoto, mas não ortodoxo, que rejeitou privadamente a doutrina da Trindade. Ele se recusou a tomar ordens sagradas na Igreja da Inglaterra, ao contrário da maioria dos membros da faculdade de Cambridge do dia. Além de seu trabalho nas ciências matemáticas, Newton dedicou grande parte de seu tempo ao estudo da alquimia e da cronologia bíblica, mas a maioria de seu trabalho nessas áreas permaneceu inédita até muito tempo depois de sua morte. Politicamente e pessoalmente ligado ao partido Whig, Newton serviu dois mandatos breves como membro do Parlamento para a Universidade de Cambridge, em 1689-1690 e 1701-1702. Ele foi condecorado pela rainha Anne em 1705 e passou as últimas três décadas de sua vida em Londres, servindo como Warden (1696-1699) e Master (1699–1727) da Royal Mint, bem como presidente da Royal Society (1703–1727)
