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
import tempfile
from datetime import timedelta
from os.path import join, isfile

from neon_solvers import AbstractSolver
from requests_cache import CachedSession


def make_speakable(summary):
    # let's remove unwanted data from parantheses
    #  - many results have (human: XX unit) ref values, remove them
    if "(human: " in summary:
        splits = summary.split("(human: ")
        for idx, s in enumerate(splits):
            splits[idx] = ")".join(s.split(")")[1:])
        summary = " ".join(splits)

    # remove duplicated units in text
    # TODO probably there's a lot more to add here....
    replaces = {
        "cm (centimeters)": "centimeters",
        "cm³ (cubic centimeters)": "cubic centimeters",
        "cm² (square centimeters)": "square centimeters",
        "mm (millimeters)": "millimeters",
        "mm² (square millimeters)": "square millimeters",
        "mm³ (cubic millimeters)": "cubic millimeters",
        "kg (kilograms)": "kilograms",
        "kHz (kilohertz)": "kilohertz",
        "ns (nanoseconds)": "nanoseconds",
        "µs (microseconds)": "microseconds",
        "m/s (meters per second)": "meters per second",
        "km/s (kilometers per second)": "kilometers per second",
        "mi/s (miles per second)": "miles per second",
        "mph (miles per hour)": "miles per hour",
        "ª (degrees)": " degrees"
    }
    for k, v in replaces.items():
        summary = summary.replace(k, v)

    # replace units, only if they are individual words
    units = {
        "cm": "centimeters",
        "cm³": "cubic centimeters",
        "cm²": "square centimeters",
        "mm": "millimeters",
        "mm²": "square millimeters",
        "mm³": "cubic millimeters",
        "kg": "kilograms",
        "kHz": "kilohertz",
        "ns": "nanoseconds",
        "µs": "microseconds",
        "m/s": "meters per second",
        "km/s": "kilometers per second",
        "mi/s": "miles per second",
        "mph": "miles per hour"
    }
    words = [w if w not in units else units[w]
             for w in summary.split(" ")]
    summary = " ".join(words)

    return summary


class WolframAlphaSolver(AbstractSolver):
    def __init__(self, config=None):
        super(WolframAlphaSolver, self).__init__(name="WolframAlpha", priority=25, config=config)
        self.appid = self.config.get("appid") or "Y7R353-9HQAAL8KKA"
        self.units = self.config.get("units") or "metric"
        self.session = CachedSession(backend="memory", expire_after=timedelta(minutes=5))

    # data api
    def get_data(self, query, context=None):
        """
       query assured to be in self.default_lang
       return a dict response
       """
        url = 'http://api.wolframalpha.com/v2/query'
        params = {"appid": self.appid,
                  "input": query,
                  "output": "json",
                  "units": self.units}
        return self.session.get(url, params=params).json()

    # image api (simple)
    def get_image(self, query, context=None):
        """
        query assured to be in self.default_lang
        return path/url to a single image to acompany spoken_answer
        """
        url = 'http://api.wolframalpha.com/v1/simple'
        params = {"appid": self.appid,
                  "i": query,
                  # "background": "F5F5F5",
                  "layout": "labelbar",
                  "units": self.units}
        path = join(tempfile.gettempdir(), query.replace(" ", "_") + ".gif")
        if not isfile(path):
            image = self.session.get(url, params=params).content
            with open(path, "wb") as f:
                f.write(image)
        return path

    # spoken answers api (spoken)
    def get_spoken_answer(self, query, context):
        """
        query assured to be in self.default_lang
        return a single sentence text response
        """
        url = 'http://api.wolframalpha.com/v1/spoken'
        params = {"appid": self.appid,
                  "i": query,
                  "units": self.units}
        answer = self.session.get(url, params=params).text
        bad_answers = ["no spoken result available",
                       "wolfram alpha did not understand your input"]
        if answer.lower().strip() in bad_answers:
            return None
        return answer

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
        # these are returned in spoken answer or otherwise unwanted
        skip = ['Input interpretation', 'Interpretation',
                'Result', 'Value', 'Image']
        steps = []

        for pod in data['queryresult'].get('pods', []):
            title = pod["title"]
            if title in skip:
                continue

            for sub in pod["subpods"]:
                subpod = {"title": title}
                summary = sub["img"]["alt"]
                subtitle = sub.get("title") or sub["img"]["title"]
                if subtitle and subtitle != summary:
                    subpod["title"] = subtitle

                if summary == title:
                    # it's an image result
                    subpod["img"] = sub["img"]["src"]
                elif summary.startswith("(") and summary.endswith(")"):
                    continue
                else:
                    subpod["summary"] = summary
                steps.append(subpod)

        # do any extra processing here
        prev = ""
        for idx, step in enumerate(steps):
            # merge steps
            if step["title"] == prev:
                summary = steps[idx - 1]["summary"] + "\n" + step["summary"]
                steps[idx]["summary"] = summary
                steps[idx]["img"] = step.get("img") or steps[idx - 1].get("img")
                steps[idx - 1] = None
            elif step.get("summary") and step["title"]:
                # inject title in speech, eg we do not want wolfram to just read family names without context
                steps[idx]["summary"] = step["title"] + ".\n" + step["summary"]

            # normalize summary
            if step.get("summary"):
                steps[idx]["summary"] = make_speakable(steps[idx]["summary"])

            prev = step["title"]
        return [s for s in steps if s]


if __name__ == "__main__":
    d = WolframAlphaSolver()

    query = "who is Isaac Newton"

    # full answer
    ans = d.spoken_answer(query)
    print(ans)
    # Sir Isaac Newton (25 December 1642 – 20 March 1726/27) was an English mathematician, physicist, astronomer, alchemist, theologian, and author (described in his time as a "natural philosopher") widely recognised as one of the greatest mathematicians and physicists of all time and among the most influential scientists.

    ans = d.visual_answer(query)
    print(ans)
    # /tmp/who_is_Isaac_Newton.gif

    # chunked answer, "tell me more"
    for sentence in d.long_answer(query):
        print("#", sentence["title"])
        print(sentence.get("summary"), sentence.get("img"))

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
    # Sir Isaac Newton (25 de dezembro de 1642 - 20 de março de 1726/27) foi um matemático, físico, astrônomo, alquimista, teólogo e autor (descrito em seu tempo como um "filósofo natural") amplamente reconhecido como um dos maiores matemáticos e físicos de todos os tempos e entre os cientistas mais influentes