from ovos_workshop.skills import OVOSSkill
from mycroft.skills import intent_handler


class PersonalSkill(OVOSSkill):
    @intent_handler("WhenWereYouBorn.intent")
    def handle_when_were_you_born_intent(self, message):
        self.speak_dialog("when.was.i.born")

    @intent_handler("WhereWereYouBorn.intent")
    def handle_where_were_you_born_intent(self, message):
        self.speak_dialog("where.was.i.born")

    @intent_handler("WhoMadeYou.intent")
    def handle_who_made_you_intent(self, message):
        self.speak_dialog("who.made.me")

    @intent_handler("WhoAreYou.intent")
    def handle_who_are_you_intent(self, message):
        name = self.config_core.get("listener", {}).get("wake_word",
                                                        "mycroft")
        name = name.lower().replace("hey ", "")
        self.speak_dialog("who.am.i", {"name": name})

    @intent_handler("WhatAreYou.intent")
    def handle_what_are_you_intent(self, message):
        self.speak_dialog("what.am.i")

    @intent_handler("DoYouRhyme.intent")
    def handle_do_you_rhyme(self, message):
        self.speak_dialog("tell.a.rhyme")

    @intent_handler("DoYouDream.intent")
    def handle_do_you_dream(self, message):
        self.speak_dialog("dream")


def create_skill():
    return PersonalSkill()
