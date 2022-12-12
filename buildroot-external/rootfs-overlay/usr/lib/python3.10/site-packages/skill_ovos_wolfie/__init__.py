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
from os.path import join

from adapt.intent import IntentBuilder
from mycroft.skills.common_query_skill import CommonQuerySkill, CQSMatchLevel
from mycroft.skills.core import intent_handler
from ovos_utils.gui import can_use_gui

from neon_solver_wolfram_alpha_plugin import WolframAlphaSolver


class WolframAlphaSkill(CommonQuerySkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wolfie = None
        # continuous dialog, "tell me more"
        self.idx = 0
        self.last_query = None
        self.results = []

        # answer processing options
        self.skip_images = True  # some wolfram results are pictures with no speech
        # if a gui is available the title is read and image displayed

        # These results are usually unwanted as spoken responses
        # they are either spammy or cant be handled by TTS properly
        self.skips = [
            # quantities, eg speed of light
            'Comparison',  # spammy
            'Corresponding quantities',  # spammy
            'Basic unit dimensions',  # TTS will fail hard 99% of time
            # when asking about word definitions
            'American pronunciation',  # can not pronounce IPA phonemes
            'Translations',  # TTS wont handle other langs or charsets
            'Hyphenation',  # spammy
            'Anagrams',  # spammy
            'Lexically close words',  # spammy
            'Overall typical frequency',  # spammy
            'Crossword puzzle clues',  # spammy
            'Scrabble score',  # spammy
            'Other notable uses'  # spammy
        ]

    def initialize(self):
        self.wolfie = WolframAlphaSolver({
            "units": self.config_core['system_unit'],
            "appid": self.settings.get("api_key")
        })

    # explicit intents
    @intent_handler("search_wolfie.intent")
    def handle_search(self, message):
        query = message.data["query"]
        response = self.ask_the_wolf(query)
        if response:
            self.speak_result()
        else:
            self.speak_dialog("no_answer")

    @intent_handler(IntentBuilder("WolfieMore").require("More").
                    require("WolfieKnows"))
    def handle_tell_more(self, message):
        """ Follow up query handler, "tell me more"."""
        self.speak_result()

    # common query integration
    def CQS_match_query_phrase(self, utt):
        self.log.debug("WolframAlpha query: " + utt)
        response = self.ask_the_wolf(utt)
        if response:
            self.idx += 1  # spoken by common query framework
            return (utt, CQSMatchLevel.GENERAL, response,
                    {'query': utt, 'answer': response})

    def CQS_action(self, phrase, data):
        """ If selected show gui """
        self.display_wolfie()

    # wolfram integration
    def ask_the_wolf(self, query):
        # context for follow up questions
        self.set_context("WolfieKnows", query)
        results = self.wolfie.long_answer(query,
                                          context={"lang": self.lang})
        self.idx = 0
        self.last_query = query
        self.results = [s for s in results if s.get("title") not in self.skips]
        if len(self.results):
            return self.results[0]["summary"]

    def display_wolfie(self):
        if not can_use_gui(self.bus):
            return
        image = None
        # issues can happen if skill reloads
        # eg. "tell me more" -> invalid self.idx
        if self.idx < len(self.results):
            image = self.results[self.idx].get("img")
        if self.last_query:
            image = image or self.wolfie.visual_answer(self.last_query,
                                                       context={"lang": self.lang})
        if image:
            self.gui["wolfram_image"] = image
            # scrollable full result page
            self.gui.show_page(join(self.root_dir, "ui", "wolf.qml"), override_idle=45)

    def speak_result(self):
        if self.idx + 1 > len(self.results):
            self.speak_dialog("thats all")
            self.remove_context("WolfieKnows")
            self.idx = 0
        else:
            if not self.results[self.idx].get("summary"):
                if not self.skip_images and can_use_gui(self.bus):
                    self.speak(self.results[self.idx]["title"])
                    self.display_wolfie()
                else:
                    # skip image only result
                    self.idx += 1
                    self.speak_result()
                    return
            else:
                self.display_wolfie()
                # make it more speech friendly
                ans = self.results[self.idx]["summary"]
                ans = ans.replace(" | ", "; ")
                self.speak(ans)
            self.idx += 1


def create_skill():
    return WolframAlphaSkill()
