from ovos_utils.messagebus import Message


class EnclosureAPI:
    """
    This API is intended to be used to interface with the hardware
    that is running Mycroft.  It exposes all possible commands which
    can be sent to a Mycroft enclosure implementation.

    Different enclosure implementations may implement this differently
    and/or may ignore certain API calls completely.  For example,
    the eyes_color() API might be ignore on a Mycroft that uses simple
    LEDs which only turn on/off, or not at all on an implementation
    where there is no face at all.
    """

    def __init__(self, bus=None, skill_id=""):
        self.bus = bus
        self.skill_id = skill_id

    def set_bus(self, bus):
        self.bus = bus

    def set_id(self, skill_id):
        self.skill_id = skill_id

    def register(self, skill_id=""):
        """Registers a skill as active. Used for speak() and speak_dialog()
        to 'patch' a previous implementation. Somewhat hacky.
        """
        skill_id = skill_id or self.skill_id
        self.bus.emit(
            Message("enclosure.active_skill",
                    data={"skill_id": skill_id},
                    context={"destination": ["enclosure"],
                             "skill_id": skill_id}))

    def reset(self):
        """The enclosure should restore itself to a started state.
        Typically this would be represented by the eyes being 'open'
        and the mouth reset to its default (smile or blank).
        """
        self.bus.emit(Message("enclosure.reset",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def system_reset(self):
        """The enclosure hardware should reset any CPUs, etc."""
        self.bus.emit(Message("enclosure.system.reset",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def system_mute(self):
        """Mute (turn off) the system speaker."""
        self.bus.emit(Message("enclosure.system.mute",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def system_unmute(self):
        """Unmute (turn on) the system speaker."""
        self.bus.emit(Message("enclosure.system.unmute",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def system_blink(self, times):
        """The 'eyes' should blink the given number of times.
        Args:
            times (int): number of times to blink
        """
        self.bus.emit(Message("enclosure.system.blink",
                              data={'times': times},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_on(self):
        """Illuminate or show the eyes."""
        self.bus.emit(Message("enclosure.eyes.on",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_off(self):
        """Turn off or hide the eyes."""
        self.bus.emit(Message("enclosure.eyes.off",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_blink(self, side):
        """Make the eyes blink
        Args:
            side (str): 'r', 'l', or 'b' for 'right', 'left' or 'both'
        """
        self.bus.emit(Message("enclosure.eyes.blink", {'side': side},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_narrow(self):
        """Make the eyes look narrow, like a squint"""
        self.bus.emit(Message("enclosure.eyes.narrow",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_look(self, side):
        """Make the eyes look to the given side
        Args:
            side (str): 'r' for right
                        'l' for left
                        'u' for up
                        'd' for down
                        'c' for crossed
        """
        self.bus.emit(Message("enclosure.eyes.look",
                              data={'side': side},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_color(self, r=255, g=255, b=255):
        """Change the eye color to the given RGB color
        Args:
            r (int): 0-255, red value
            g (int): 0-255, green value
            b (int): 0-255, blue value
        """
        self.bus.emit(Message("enclosure.eyes.color",
                              data={'r': r, 'g': g, 'b': b},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_setpixel(self, idx, r=255, g=255, b=255):
        """Set individual pixels of the Mark 1 neopixel eyes
        Args:
            idx (int): 0-11 for the right eye, 12-23 for the left
            r (int): The red value to apply
            g (int): The green value to apply
            b (int): The blue value to apply
        """
        if idx < 0 or idx > 23:
            raise ValueError(f'idx ({idx}) must be between 0-23')
        self.bus.emit(Message("enclosure.eyes.setpixel",
                              data={'idx': idx, 'r': r, 'g': g, 'b': b},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_fill(self, percentage):
        """Use the eyes as a type of progress meter
        Args:
            percentage (int): 0-49 fills the right eye, 50-100 also covers left
        """
        if percentage < 0 or percentage > 100:
            raise ValueError(f'percentage ({percentage}) must be between 0-100')
        self.bus.emit(Message("enclosure.eyes.fill",
                              data={'percentage': percentage},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_brightness(self, level=30):
        """Set the brightness of the eyes in the display.
        Args:
            level (int): 1-30, bigger numbers being brighter
        """
        self.bus.emit(Message("enclosure.eyes.level", {'level': level},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_reset(self):
        """Restore the eyes to their default (ready) state."""
        self.bus.emit(Message("enclosure.eyes.reset",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_spin(self):
        """Make the eyes 'roll'
        """
        self.bus.emit(Message("enclosure.eyes.spin",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_timed_spin(self, length):
        """Make the eyes 'roll' for the given time.
        Args:
            length (int): duration in milliseconds of roll, None = forever
        """
        self.bus.emit(Message("enclosure.eyes.timedspin",
                              data={'length': length},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def eyes_volume(self, volume):
        """Indicate the volume using the eyes
        Args:
            volume (int): 0 to 11
        """
        if volume < 0 or volume > 11:
            raise ValueError('volume ({}) must be between 0-11'.
                             format(str(volume)))
        self.bus.emit(Message("enclosure.eyes.volume",
                              data={'volume': volume},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_reset(self):
        """Restore the mouth display to normal (blank)"""
        self.bus.emit(Message("enclosure.mouth.reset",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_talk(self):
        """Show a generic 'talking' animation for non-synched speech"""
        self.bus.emit(Message("enclosure.mouth.talk",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_think(self):
        """Show a 'thinking' image or animation"""
        self.bus.emit(Message("enclosure.mouth.think",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_listen(self):
        """Show a 'thinking' image or animation"""
        self.bus.emit(Message("enclosure.mouth.listen",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_smile(self):
        """Show a 'smile' image or animation"""
        self.bus.emit(Message("enclosure.mouth.smile",
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_viseme(self, start, viseme_pairs):
        """ Send mouth visemes as a list in a single message.

            Args:
                start (int):    Timestamp for start of speech
                viseme_pairs:   Pairs of viseme id and cumulative end times
                                (code, end time)

                                codes:
                                 0 = shape for sounds like 'y' or 'aa'
                                 1 = shape for sounds like 'aw'
                                 2 = shape for sounds like 'uh' or 'r'
                                 3 = shape for sounds like 'th' or 'sh'
                                 4 = neutral shape for no sound
                                 5 = shape for sounds like 'f' or 'v'
                                 6 = shape for sounds like 'oy' or 'ao'
        """
        self.bus.emit(Message("enclosure.mouth.viseme_list",
                              data={"start": start,
                                    "visemes": viseme_pairs},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_text(self, text=""):
        """Display text (scrolling as needed)
        Args:
            text (str): text string to display
        """
        self.bus.emit(Message("enclosure.mouth.text",
                              data={'text': text},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_display(self, img_code="", x=0, y=0, refresh=True):
        """Display images on faceplate. Currently supports images up to 16x8,
           or half the face. You can use the 'x' parameter to cover the other
           half of the faceplate.
        Args:
            img_code (str): text string that encodes a black and white image
            x (int): x offset for image
            y (int): y offset for image
            refresh (bool): specify whether to clear the faceplate before
                            displaying the new image or not.
                            Useful if you'd like to display multiple images
                            on the faceplate at once.
        """
        self.bus.emit(Message('enclosure.mouth.display',
                              data={'img_code': img_code,
                                    'xOffset': x,
                                    'yOffset': y,
                                    'clearPrev': refresh},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def mouth_display_png(self, image_absolute_path,
                          invert=False, x=0, y=0, refresh=True):
        """ Send an image to the enclosure.

        Args:
            image_absolute_path (string): The absolute path of the image
            invert (bool): inverts the image being drawn.
            x (int): x offset for image
            y (int): y offset for image
            refresh (bool): specify whether to clear the faceplate before
                            displaying the new image or not.
                            Useful if you'd like to display muliple images
                            on the faceplate at once.
            """
        self.bus.emit(Message("enclosure.mouth.display_image",
                              data={'img_path': image_absolute_path,
                                    'xOffset': x,
                                    'yOffset': y,
                                    'invert': invert,
                                    'clearPrev': refresh},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def weather_display(self, img_code, temp):
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
        self.bus.emit(Message("enclosure.weather.display",
                              data={'img_code': img_code, 'temp': temp},
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def activate_mouth_events(self):
        """Enable movement of the mouth with speech"""
        self.bus.emit(Message('enclosure.mouth.events.activate',
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def deactivate_mouth_events(self):
        """Disable movement of the mouth with speech"""
        self.bus.emit(Message('enclosure.mouth.events.deactivate',
                              context={"destination": ["enclosure"],
                                       "skill_id": self.skill_id}))

    def get_eyes_color(self):
        """Get the eye RGB color for all pixels
        Returns:
           (list) pixels - list of (r,g,b) tuples for each eye pixel
        """
        message = Message("enclosure.eyes.rgb.get",
                          context={"source": "enclosure_api",
                                   "destination": "enclosure"})
        response = self.bus.wait_for_response(message, "enclosure.eyes.rgb")
        if response:
            return response.data["pixels"]
        raise TimeoutError("Enclosure took too long to respond")

    def get_eyes_pixel_color(self, idx):
        """Get the RGB color for a specific eye pixel
        Returns:
            (r,g,b) tuples for selected pixel
        """
        if idx < 0 or idx > 23:
            raise ValueError(f'idx ({idx}) must be between 0-23')
        return self.get_eyes_color()[idx]
