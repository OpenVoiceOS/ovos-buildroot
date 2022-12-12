from gpiozero import LED
from ovos_PHAL_plugin_respeaker_4mic.drivers import get_pixel_ring
from time import sleep

from ovos_PHAL.detection import is_respeaker_4mic
from ovos_plugin_manager.phal import PHALPlugin


class Respeaker4MicValidator:
    @staticmethod
    def validate(config=None):
        # TODO does it work for 2 and 6 mic ?
        return is_respeaker_4mic()


class Respeaker4MicControlPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-respeaker-4mic", config=config)
        self.power = LED(5)
        self.power.on()
        self.pixel_ring = get_pixel_ring()
        self.pixel_ring.set_brightness(10)
        self.pixel_ring.change_pattern('echo')
        self.pixel_ring.wakeup()
        sleep(1.5)
        self.pixel_ring.off()

    def on_record_begin(self, message=None):
        self.pixel_ring.listen()

    def on_record_end(self, message=None):
        self.on_reset(message)

    def on_audio_output_start(self, message=None):
        self.pixel_ring.speak()

    def on_audio_output_end(self, message=None):
        self.on_reset(message)

    def on_think(self, message=None):
        self.pixel_ring.think()

    def on_reset(self, message=None):
        self.pixel_ring.off()

    def on_system_reset(self, message=None):
        self.on_reset(message)

    def shutdown(self):
        self.pixel_ring.off()
        self.power.off()
        super().shutdown()
