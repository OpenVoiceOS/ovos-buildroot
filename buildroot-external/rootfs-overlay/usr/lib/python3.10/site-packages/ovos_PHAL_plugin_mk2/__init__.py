from ovos_PHAL.detection import is_mycroft_sj201
from ovos_PHAL_plugin_mk2.fan import FanControl, TemperatureMonitorThread
from ovos_PHAL_plugin_mk2.leds import ChaseLedAnimation, LedAnimation, \
    PulseLedAnimation, Led, Palette, LedThread
from ovos_PHAL_plugin_mk2.switch import Switch
from ovos_plugin_manager.phal import PHALPlugin
from mycroft_bus_client.message import Message
import time
from ovos_utils.log import LOG


class MycroftMark2Validator:
    @staticmethod
    def validate(config=None):
        # check i2c to determine if sj201 is connected
        return is_mycroft_sj201()


class MycroftMark2(PHALPlugin):
    validator = MycroftMark2Validator

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-mk2", config=config)
        self.fan = FanControl()
        self.leds = Led()
        self.switches = Switch()
        self.switches.user_mute_handler = self._on_mute
        self._last_mute = -1
        self.switches.user_action_handler = self.on_button_press
        self.switches.user_voldown_handler = self.on_button_voldown_press
        self.switches.user_volup_handler = self.on_button_volup_press
        self._last_press = 0

        # start the temperature monitor thread
        self.temperatureMonitorThread = TemperatureMonitorThread(self.fan)
        self.temperatureMonitorThread.start()

        # init leds all turned off
        self.turn_off_leds()
        self.led_thread = LedThread(self.leds,
                                    animations={
                                        "pulse": PulseLedAnimation(self.leds, Palette),
                                        "chase": ChaseLedAnimation(self.leds,
                                                                   background_color=Palette.BLUE,
                                                                   foreground_color=Palette.BLACK,
                                                                   ),
                                    })
        self.led_thread.start()
        if self.switches.SW_MUTE == 1:
            self.on_hardware_mute()

    def shutdown(self):
        self.temperatureMonitorThread.exit_flag.set()
        super().shutdown()

    def _on_mute(self, val):
        LOG.debug("Mark2:HardwareEnclosure:handle_mute() - val = %s" % (val,))
        if val != self._last_mute:
            self._last_mute = val
            if val == 0:
                self.on_hardware_unmute()
            else:
                self.on_hardware_mute()

    def on_button_press(self):
        LOG.debug("SJ201 Listen button pressed")
        # debounce this 10 seconds
        if time.time() - self._last_press > 10:
            self._last_press = time.time()
            self.bus.emit(Message("mycroft.mic.listen"))

    def on_button_volup_press(self):
        LOG.debug("SJ201 VolumeUp button pressed")
        self.bus.emit(Message("mycroft.volume.increase"))

    def on_button_voldown_press(self):
        LOG.debug("SJ201 VolumeDown button pressed")
        self.bus.emit(Message("mycroft.volume.decrease"))

    def on_hardware_mute(self):
        """Called when hardware switch is set to mute"""
        # Triggers red border
        self.bus.emit(Message("mycroft.mic.mute"))
        self.leds.fill(Palette.BURNT_ORANGE)

    def on_hardware_unmute(self):
        """Called when hardware switch is set to unmute"""
        # Removes red border
        self.bus.emit(Message("mycroft.mic.unmute"))
        self.turn_off_leds()

    def turn_off_leds(self):
        self.leds.fill(Palette.BLACK)

    # Audio Events
    def on_awake(self, message=None):
        ''' on wakeup animation '''
        # TODO new led animation

    def on_sleep(self, message=None):
        ''' on naptime animation '''
        # TODO new led animation
        self.turn_off_leds()

    def on_reset(self, message=None):
        """The enclosure should restore itself to a started state.
        Typically this would be represented by the eyes being 'open'
        and the mouth reset to its default (smile or blank).
        """
        self.turn_off_leds()

    def on_record_begin(self, message=None):
        self.led_thread.start_animation("pulse")

    def on_record_end(self, message=None):
        self.led_thread.stop_animation("pulse")

    # System Events
    def on_system_reset(self, message=None):
        """The enclosure hardware should reset any CPUs, etc."""
        self.turn_off_leds()
