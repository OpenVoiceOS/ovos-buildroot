import time
from ovos_utils import camel_case_split
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
from ovos_config import Configuration
from ovos_plugin_manager.utils.config import get_plugin_config


class PHALValidator:
    @staticmethod
    def validate(config=None):
        """ this method is called before loading the plugin.
        If it returns False the plugin is not loaded.
        This allows a plugin to run platform checks"""
        return config.get("enabled", True)


class PHALPlugin:
    """
    This base class is intended to be used to interface with the hardware
    that is running Mycroft.  It exposes all possible commands which
    are expected be sent to a PHAL plugin.
    All of the handlers are optional and for convenience only
    """
    validator = PHALValidator

    def __init__(self, bus=None, name="", config=None):
        self.config_core = Configuration()
        name = name or camel_case_split(self.__class__.__name__).replace(" ", "-").lower()
        self.config = config or get_plugin_config(self.config_core,
                                                  "PHAL", name)
        self._mouth_events = False
        self._running = False
        self.bus = bus or get_mycroft_bus()
        self.log = LOG
        self.name = name

        self.bus.on("enclosure.reset", self.on_reset)

        # enclosure commands for Mycroft's Hardware.
        self.bus.on("enclosure.system.reset", self.on_system_reset)
        self.bus.on("enclosure.system.mute", self.on_system_mute)
        self.bus.on("enclosure.system.unmute", self.on_system_unmute)
        self.bus.on("enclosure.system.blink", self.on_system_blink)

        # enclosure commands for eyes
        self.bus.on('enclosure.eyes.on', self.on_eyes_on)
        self.bus.on('enclosure.eyes.off', self.on_eyes_off)
        self.bus.on('enclosure.eyes.blink', self.on_eyes_blink)
        self.bus.on('enclosure.eyes.narrow', self.on_eyes_narrow)
        self.bus.on('enclosure.eyes.look', self.on_eyes_look)
        self.bus.on('enclosure.eyes.color', self.on_eyes_color)
        self.bus.on('enclosure.eyes.level', self.on_eyes_brightness)
        self.bus.on('enclosure.eyes.volume', self.on_eyes_volume)
        self.bus.on('enclosure.eyes.spin', self.on_eyes_spin)
        self.bus.on('enclosure.eyes.timedspin', self.on_eyes_timed_spin)
        self.bus.on('enclosure.eyes.reset', self.on_eyes_reset)
        self.bus.on('enclosure.eyes.setpixel', self.on_eyes_set_pixel)
        self.bus.on('enclosure.eyes.fill', self.on_eyes_fill)

        # enclosure commands for mouth
        self.bus.on("enclosure.mouth.events.activate", self._activate_mouth_events)
        self.bus.on("enclosure.mouth.events.deactivate", self._deactivate_mouth_events)
        self.bus.on("enclosure.mouth.talk", self._on_mouth_talk)
        self.bus.on("enclosure.mouth.think", self._on_mouth_think)
        self.bus.on("enclosure.mouth.listen", self._on_mouth_listen)
        self.bus.on("enclosure.mouth.smile", self._on_mouth_smile)
        self.bus.on("enclosure.mouth.viseme", self._on_mouth_viseme)

        # mouth/matrix display
        self.bus.on("enclosure.mouth.reset", self.on_display_reset)
        self.bus.on("enclosure.mouth.text", self.on_text)
        self.bus.on("enclosure.mouth.display", self.on_display)
        self.bus.on("enclosure.weather.display", self.on_weather_display)

        # audio events
        self.bus.on('recognizer_loop:record_begin', self.on_record_begin)
        self.bus.on('recognizer_loop:record_end', self.on_record_end)
        self.bus.on("recognizer_loop:sleep", self.on_sleep)
        self.bus.on('recognizer_loop:audio_output_start', self.on_audio_output_start)
        self.bus.on('recognizer_loop:audio_output_end', self.on_audio_output_end)

        # other events
        self.bus.on("mycroft.awoken", self.on_awake)
        self.bus.on("speak", self.on_speak)
        self.bus.on("enclosure.notify.no_internet", self.on_no_internet)

        self._activate_mouth_events()

    def emit(self, msg_type, msg_data=None):
        skill_id = f"ovos.PHAL.{self.name}"
        self.bus.emit(f"{skill_id}.{msg_type}", msg_data, {"skill_id": skill_id})

    def shutdown(self):
        self.bus.remove("enclosure.reset", self.on_reset)
        self.bus.remove("enclosure.system.reset", self.on_system_reset)
        self.bus.remove("enclosure.system.mute", self.on_system_mute)
        self.bus.remove("enclosure.system.unmute", self.on_system_unmute)
        self.bus.remove("enclosure.system.blink", self.on_system_blink)

        self.bus.remove("enclosure.eyes.on", self.on_eyes_on)
        self.bus.remove("enclosure.eyes.off", self.on_eyes_off)
        self.bus.remove("enclosure.eyes.blink", self.on_eyes_blink)
        self.bus.remove("enclosure.eyes.narrow", self.on_eyes_narrow)
        self.bus.remove("enclosure.eyes.look", self.on_eyes_look)
        self.bus.remove("enclosure.eyes.color", self.on_eyes_color)
        self.bus.remove("enclosure.eyes.brightness", self.on_eyes_brightness)
        self.bus.remove("enclosure.eyes.reset", self.on_eyes_reset)
        self.bus.remove("enclosure.eyes.timedspin", self.on_eyes_timed_spin)
        self.bus.remove("enclosure.eyes.volume", self.on_eyes_volume)
        self.bus.remove("enclosure.eyes.spin", self.on_eyes_spin)
        self.bus.remove("enclosure.eyes.set_pixel", self.on_eyes_set_pixel)

        self.bus.remove("enclosure.mouth.reset", self.on_display_reset)
        self.bus.remove("enclosure.mouth.talk", self.on_talk)
        self.bus.remove("enclosure.mouth.think", self.on_think)
        self.bus.remove("enclosure.mouth.listen", self.on_listen)
        self.bus.remove("enclosure.mouth.smile", self.on_smile)
        self.bus.remove("enclosure.mouth.viseme", self.on_viseme)
        self.bus.remove("enclosure.mouth.text", self.on_text)
        self.bus.remove("enclosure.mouth.display", self.on_display)
        self.bus.remove("enclosure.mouth.events.activate", self._activate_mouth_events)
        self.bus.remove("enclosure.mouth.events.deactivate", self._deactivate_mouth_events)

        self.bus.remove("enclosure.weather.display", self.on_weather_display)

        self.bus.remove("mycroft.awoken", self.on_awake)
        self.bus.remove("recognizer_loop:sleep", self.on_sleep)
        self.bus.remove("speak", self.on_speak)
        self.bus.remove('recognizer_loop:record_begin', self.on_record_begin)
        self.bus.remove('recognizer_loop:record_end', self.on_record_end)
        self.bus.remove('recognizer_loop:audio_output_start', self.on_audio_output_start)
        self.bus.remove("enclosure.notify.no_internet", self.on_no_internet)

        self._deactivate_mouth_events()
        self._running = False

    def run(self):
        ''' start enclosure '''
        self._running = True
        while self._running:
            time.sleep(1)

    # Audio Events
    def on_record_begin(self, message=None):
        ''' listening started '''
        pass

    def on_record_end(self, message=None):
        ''' listening ended '''
        pass

    def on_audio_output_start(self, message=None):
        ''' speaking started '''
        pass

    def on_audio_output_end(self, message=None):
        ''' speaking started '''
        pass

    def on_awake(self, message=None):
        ''' on wakeup animation '''
        pass

    def on_sleep(self, message=None):
        ''' on naptime animation '''
        # TODO naptime skill animation should be ond here
        pass

    def on_speak(self, message=None):
        ''' on speak messages, intended for enclosures that disregard
        visemes '''
        pass

    def on_reset(self, message=None):
        """The enclosure should restore itself to a started state.
        Typically this would be represented by the eyes being 'open'
        and the mouth reset to its default (smile or blank).
        """
        pass

    # System Events
    def on_no_internet(self, message=None):
        """

        Args:
            message:
        """
        pass

    def on_system_reset(self, message=None):
        """The enclosure hardware should reset any CPUs, etc."""
        pass

    def on_system_mute(self, message=None):
        """Mute (turn off) the system speaker."""
        pass

    def on_system_unmute(self, message=None):
        """Unmute (turn on) the system speaker."""
        pass

    def on_system_blink(self, message=None):
        """The 'eyes' should blink the given number of times.
        Args:
            times (int): number of times to blink
        """
        pass

    # Eyes events
    def on_eyes_on(self, message=None):
        """Illuminate or show the eyes."""
        pass

    def on_eyes_off(self, message=None):
        """Turn off or hide the eyes."""
        pass

    def on_eyes_fill(self, message=None):
        pass

    def on_eyes_blink(self, message=None):
        """Make the eyes blink
        Args:
            side (str): 'r', 'l', or 'b' for 'right', 'left' or 'both'
        """
        pass

    def on_eyes_narrow(self, message=None):
        """Make the eyes look narrow, like a squint"""
        pass

    def on_eyes_look(self, message=None):
        """Make the eyes look to the given side
        Args:
            side (str): 'r' for right
                        'l' for left
                        'u' for up
                        'd' for down
                        'c' for crossed
        """
        pass

    def on_eyes_color(self, message=None):
        """Change the eye color to the given RGB color
        Args:
            r (int): 0-255, red value
            g (int): 0-255, green value
            b (int): 0-255, blue value
        """
        pass

    def on_eyes_brightness(self, message=None):
        """Set the brightness of the eyes in the display.
        Args:
            level (int): 1-30, bigger numbers being brighter
        """
        pass

    def on_eyes_reset(self, message=None):
        """Restore the eyes to their default (ready) state."""
        pass

    def on_eyes_timed_spin(self, message=None):
        """Make the eyes 'roll' for the given time.
        Args:
            length (int): duration in milliseconds of roll, None = forever
        """
        pass

    def on_eyes_volume(self, message=None):
        """Indicate the volume using the eyes
        Args:
            volume (int): 0 to 11
        """
        pass

    def on_eyes_spin(self, message=None):
        """
        Args:
        """
        pass

    def on_eyes_set_pixel(self, message=None):
        """
        Args:
        """
        pass

    # Mouth events
    def _on_mouth_reset(self, message=None):
        """Restore the mouth display to normal (blank)"""
        if self.mouth_events_active:
            self.on_display_reset(message)

    def _on_mouth_talk(self, message=None):
        """Show a generic 'talking' animation for non-synched speech"""
        if self.mouth_events_active:
            self.on_talk(message)

    def _on_mouth_think(self, message=None):
        """Show a 'thinking' image or animation"""
        if self.mouth_events_active:
            self.on_think(message)

    def _on_mouth_listen(self, message=None):
        """Show a 'thinking' image or animation"""
        if self.mouth_events_active:
            self.on_listen(message)

    def _on_mouth_smile(self, message=None):
        """Show a 'smile' image or animation"""
        if self.mouth_events_active:
            self.on_smile(message)

    def _on_mouth_viseme(self, message=None):
        """Display a viseme mouth shape for synched speech
        Args:
            code (int):  0 = shape for sounds like 'y' or 'aa'
                         1 = shape for sounds like 'aw'
                         2 = shape for sounds like 'uh' or 'r'
                         3 = shape for sounds like 'th' or 'sh'
                         4 = neutral shape for no sound
                         5 = shape for sounds like 'f' or 'v'
                         6 = shape for sounds like 'oy' or 'ao'
        """
        if self.mouth_events_active:
            self.on_viseme(message)

    def _on_mouth_text(self, message=None):
        """Display text (scrolling as needed)
        Args:
            text (str): text string to display
        """
        if self.mouth_events_active:
            self.on_text(message)

    def _on_mouth_display(self, message=None):
        if self.mouth_events_active:
            self.on_display(message)

    # Display (faceplate) events
    def on_display_reset(self, message=None):
        """Restore the mouth display to normal (blank)"""
        pass

    def on_talk(self, message=None):
        """Show a generic 'talking' animation for non-synched speech"""
        pass

    def on_think(self, message=None):
        """Show a 'thinking' image or animation"""
        pass

    def on_listen(self, message=None):
        """Show a 'thinking' image or animation"""
        pass

    def on_smile(self, message=None):
        """Show a 'smile' image or animation"""
        pass

    def on_viseme(self, message=None):
        """Display a viseme mouth shape for synched speech
        Args:
            code (int):  0 = shape for sounds like 'y' or 'aa'
                         1 = shape for sounds like 'aw'
                         2 = shape for sounds like 'uh' or 'r'
                         3 = shape for sounds like 'th' or 'sh'
                         4 = neutral shape for no sound
                         5 = shape for sounds like 'f' or 'v'
                         6 = shape for sounds like 'oy' or 'ao'
        """
        pass

    def on_text(self, message=None):
        """Display text (scrolling as needed)
        Args:
            text (str): text string to display
        """
        pass

    def on_display(self, message=None):
        """Display images on faceplate. Currently supports images up to 16x8,
           or half the face. You can use the 'x' parameter to cover the other
           half of the faceplate.
        Args:
            img_code (str): text string that encodes a black and white image
            x (int): x offset for image
            y (int): y offset for image
            refresh (bool): specify whether to clear the faceplate before
                            displaying the new image or not.
                            Useful if you'd like to display muliple images
                            on the faceplate at once.
        """
        pass

    def on_weather_display(self, message=None):
        """Show a the temperature and a weather icon

        Args:
            img_code (char): one of the following icon codes
                         0 = sunny
                         1 = partly cloudy
                         2 = cloudy
                         3 = light rain
                         4 = raining
                         5 = stormy
                         6 = snowing
                         7 = wind/mist
            temp (int): the temperature (either C or F, not indicated)
        """
        pass

    @property
    def mouth_events_active(self):
        return self._mouth_events

    def _activate_mouth_events(self, message=None):
        """Enable movement of the mouth with speech"""
        self._mouth_events = True

    def _deactivate_mouth_events(self, message=None):
        """Disable movement of the mouth with speech"""
        self._mouth_events = False


# Just for api consistency
AdminPlugin = PHALPlugin
AdminValidator = PHALValidator
