from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util import normalize
from mycroft.util.parse import extract_number


class VolumeSkill(MycroftSkill):

    # intents
    @intent_handler(IntentBuilder("change_volume").require('change_volume'))
    def handle_change_volume_intent(self, message):
        utterance = message.data['utterance']
        volume_change = extract_number(normalize(utterance))
        self.bus.emit(message.forward("mycroft.volume.set",
                                      {"percent": volume_change / 100}))
        if volume_change >= 100:
            self.speak_dialog('max.volume')
        else:
            self.speak_dialog('set.volume.percent',
                              data={'level': volume_change})

    @intent_handler(IntentBuilder("less_volume").require('less_volume'))
    def handle_less_volume_intent(self, message):
        utterance = message.data['utterance']
        volume_change = extract_number(normalize(utterance))
        self.bus.emit(message.forward("mycroft.volume.decrease",
                                      {"percent": volume_change / 100}))

    @intent_handler(IntentBuilder("increase_volume").require('increase_volume'))
    def handle_increase_volume_intent(self, message):
        utterance = message.data['utterance']
        volume_change = extract_number(normalize(utterance))
        self.bus.emit(message.forward("mycroft.volume.increase",
                                      {"percent": volume_change / 100}))

    @intent_file_handler('max_volume.intent')
    def handle_max_volume_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.set",
                                      {"percent": 1.0}))
        self.speak_dialog('max.volume')

    @intent_file_handler('high_volume.intent')
    def handle_high_volume_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.set",
                                      {"percent": 0.9}))

    @intent_file_handler('default_volume.intent')
    def handle_default_volume_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.set",
                                      {"percent": 0.7}))

    @intent_file_handler('low_volume.intent')
    def handle_low_volume_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.set",
                                      {"percent": 0.3}))

    @intent_file_handler('mute.intent')
    def handle_mute_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.mute"))

    @intent_file_handler('unmute.intent')
    def handle_unmute_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.unmute"))

    @intent_file_handler('toggle_mute.intent')
    def handle_toggle_unmute_intent(self, message):
        self.bus.emit(message.forward("mycroft.volume.mute.toggle"))

    @intent_handler(IntentBuilder("current_volume").require('current_volume'))
    def handle_query_volume(self, message):
        response = self.bus.wait_for_response(message.forward("volume.get"))
        if response:
            volume = response.data["percent"] * 100
            self.speak_dialog('volume.is', data={'volume': volume})
        else:
            # TODO dedicated error dialog
            raise TimeoutError("Failed to get volume")


def create_skill():
    return VolumeSkill()
