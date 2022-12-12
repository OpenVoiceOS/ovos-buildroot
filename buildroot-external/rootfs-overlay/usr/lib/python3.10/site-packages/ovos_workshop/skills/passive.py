from ovos_workshop.skills.active import ActiveSkill


class PassiveSkill(ActiveSkill):

    def handle_utterance(self, utterances, lang="en-us"):
        """ Listen to all utterances passively, eg, take metrics """

    def converse(self, utterances, lang="en-us"):
        self.handle_utterance(utterances, lang)
        return False
