# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from ovos_utils.gui import can_use_gui
from adapt.intent import IntentBuilder
from mycroft.skills.common_query_skill import CommonQuerySkill, CQSMatchLevel
from mycroft.skills.core import intent_handler
from neon_solver_ddg_plugin import DDGSolver


class DuckDuckGoSkill(CommonQuerySkill):
    def __init__(self):
        super().__init__()
        self.duck = DDGSolver()
        # for usage in tell me more / follow up questions
        self.idx = 0
        self.results = []
        self.image = None

    # intents
    @intent_handler("search_duck.intent")
    def handle_search(self, message):
        query = message.data["query"]
        summary = self.ask_the_duck(query)
        if summary:
            self.speak_result()
        else:
            self.speak_dialog("no_answer")

    @intent_handler(IntentBuilder("DuckMore").require("More").
                    require("DuckKnows"))
    def handle_tell_more(self, message):
        """ Follow up query handler, "tell me more"."""
        # query = message.data["DuckKnows"]
        # data, related_queries = self.duck.get_infobox(query)
        # TODO maybe do something with the infobox data ?
        self.speak_result()

    # common query
    def CQS_match_query_phrase(self, utt):
        summary = self.ask_the_duck(utt)
        if summary:
            self.idx += 1  # spoken by common query
            return (utt, CQSMatchLevel.GENERAL, summary,
                    {'query': utt,
                     'image': self.image,
                     'answer': summary})

    def CQS_action(self, phrase, data):
        """ If selected show gui """
        self.display_ddg(data["answer"], data["image"])

    # duck duck go api
    def ask_the_duck(self, query):
        # context for follow up questions
        self.set_context("DuckKnows", query)
        self.idx = 0
        self.results = self.duck.long_answer(query, lang=self.lang)
        self.image = self.duck.get_image(query)
        if self.results:
            return self.results[0]["summary"]

    def display_ddg(self, summary=None, image=None):
        if not can_use_gui(self.bus):
            return
        image = image or \
                self.image or \
                "https://github.com/JarbasSkills/skill-ddg/raw/master/ui/logo.png"
        if image.startswith("/"):
            image = "https://duckduckgo.com" + image
        self.gui['summary'] = summary or ""
        self.gui['imgLink'] = image
        self.gui.show_page("DuckDelegate.qml", override_idle=60)

    def speak_result(self):
        if self.idx + 1 > len(self.results):
            self.speak_dialog("thats all")
            self.remove_context("DuckKnows")
            self.idx = 0
        else:
            self.display_ddg(self.results[self.idx]["summary"],
                             self.results[self.idx]["img"])
            self.speak(self.results[self.idx]["summary"])
            self.idx += 1


def create_skill():
    return DuckDuckGoSkill()
