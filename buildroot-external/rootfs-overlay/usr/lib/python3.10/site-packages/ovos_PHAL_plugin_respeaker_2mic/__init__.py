from mycroft_bus_client.message import Message
from ovos_PHAL.detection import is_respeaker_2mic
from ovos_plugin_manager.phal import PHALPlugin
from ovos_PHAL_plugin_respeaker_2mic.drivers import get_led, get_button


class Respeaker2MicValidator:
    @staticmethod
    def validate(config=None):
        # TODO does it work for 2 and 6 mic ?
        return is_respeaker_2mic()


class Respeaker2MicControlPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-respeaker-2mic", config=config)
        self.button = get_button()
        self.button.on_press(self.handle_button_press)
        self.button.on_button_down(self.handle_button_down)
        self.button.on_button_up(self.handle_button_up)
        self.led = get_led()
        self.led.wakeup()

    def handle_button_press(self, press_time=0):
        self.bus.emit(Message("ovos.PHAL.button.press",
                              {"press_time": press_time},
                              {"skill_id": self.name}))

    def handle_button_down(self):
        self.bus.emit(Message("ovos.PHAL.button.down",
                              {"skill_id": self.name}))

    def handle_button_up(self):
        self.bus.emit(Message("ovos.PHAL.button.up",
                              {"skill_id": self.name}))

    def on_record_begin(self, message=None):
        self.led.listen()

    def on_record_end(self, message=None):
        self.on_reset(message)

    def on_audio_output_start(self, message=None):
        self.led.speak()

    def on_audio_output_end(self, message=None):
        self.on_reset(message)

    def on_think(self, message=None):
        self.led.think()

    def on_reset(self, message=None):
        self.led.off()

    def on_system_reset(self, message=None):
        self.on_reset(message)

    def shutdown(self):
        self.led.off()
        super().shutdown()
