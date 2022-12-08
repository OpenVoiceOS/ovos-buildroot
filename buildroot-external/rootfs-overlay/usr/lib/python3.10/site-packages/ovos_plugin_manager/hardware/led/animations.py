from abc import abstractmethod
from threading import Event

from ovos_utils.log import LOG
from time import time, sleep
from typing import Optional

from ovos_plugin_manager.hardware.led import AbstractLed, Color


class LedAnimation:
    def __init__(self, leds: AbstractLed, **kwargs):
        self.leds = leds

    @abstractmethod
    def start(self, timeout: Optional[int] = None, one_shot: bool = False):
        """
        Start the animation.
        :param timeout: Optional timeout in seconds after which animation stops
        :param one_shot: if True, run animation once and return
        """

    @abstractmethod
    def stop(self):
        """
        Stop the animation and reset LEDs to black.
        """


class BreatheLedAnimation(LedAnimation):
    def __init__(self, leds: AbstractLed, color: Color):
        """
        Breathing effect where all LEDs dim up and down until timing out
        or being stopped. LEDs are turned off after animation.
        @param leds: LED object to interact with
        @param color: Base color of LEDs
        """
        LedAnimation.__init__(self, leds)
        self.color = color
        self.step = 0.05
        self.step_delay = 0.05
        self.stopping = Event()

    def start(self, timeout=None, one_shot=False):
        self.stopping.clear()
        end_time = time() + timeout if timeout else None
        brightness = 1
        step = -1 * self.step
        ending = False
        while not self.stopping.is_set():
            if brightness >= 1:  # Going Down
                step = -1 * self.step
            elif brightness <= 0:
                step = self.step

            brightness += step
            self.leds.fill(tuple(brightness * part for part in
                                 self.color.as_rgb_tuple()))
            sleep(self.step_delay)
            if one_shot and brightness >= 1:
                ending = True
            elif ending and brightness <= 0:
                self.stopping.set()
            elif end_time and time() > end_time:
                self.stopping.set()
        self.leds.fill(Color.BLACK.as_rgb_tuple())

    def stop(self):
        self.stopping.set()


class ChaseLedAnimation(LedAnimation):
    def __init__(self, leds: AbstractLed, foreground_color: Color,
                 background_color: Color = Color.BLACK):
        """
        Chase effect where all LEDs are lit individually in order until timing
        out or being stopped. LEDs are turned off after animation.
        @param leds: LED object to interact with
        @param foreground_color: Color of active LED
        @param background_color: Color of inactive LEDs
        """
        LedAnimation.__init__(self, leds)
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.step = 0.05
        self.step_delay = 0.1
        self.stopping = Event()

    def start(self, timeout=None, one_shot=False):
        self.stopping.clear()
        end_time = time() + timeout if timeout else None

        self.leds.fill(self.background_color.as_rgb_tuple())
        while not self.stopping.is_set():
            for led in range(0, self.leds.num_leds):
                self.leds.set_led(led, self.foreground_color.as_rgb_tuple())
                sleep(self.step_delay)
                self.leds.set_led(led, self.background_color.as_rgb_tuple())
            if one_shot:
                self.stopping.set()
            elif end_time and time() > end_time:
                self.stopping.set()
        self.leds.fill(Color.BLACK.as_rgb_tuple())

    def stop(self):
        self.stopping.set()


class FillLedAnimation(LedAnimation):
    def __init__(self, leds: AbstractLed, fill_color: Color,
                 reverse: bool = False):
        """
        Fill effect where LEDs are set to the same color in order. LEDs will
        remain lit after the animation.
        @param leds: LED object to interact with
        @param fill_color: Color to fill LEDs
        @param reverse: If true, fill in reverse order
        """
        LedAnimation.__init__(self, leds)
        self.fill_color = fill_color
        self.reverse = reverse
        self.step_delay = 0.05

    def start(self, timeout=None, one_shot=True):
        if not one_shot or timeout is not None:
            LOG.warning("Fill animation does not support persistent animation")
        leds = list(range(0, self.leds.num_leds))
        if self.reverse:
            leds.reverse()
        for led in leds:
            self.leds.set_led(led, self.fill_color.as_rgb_tuple())
            sleep(self.step_delay)

    def stop(self):
        pass


class RefillLedAnimation(LedAnimation):
    def __init__(self, leds: AbstractLed, fill_color: Color,
                 reverse: bool = False):
        """
        Fill effect in the requested color, followed by fill effect in black.
        Animation repeats until timing out or being stopped. LEDs are turned
        off after animation.
        @param leds: LED object to interact with
        @param fill_color: Color to fill LEDs
        @param reverse: If true, fill in reverse order
        """
        LedAnimation.__init__(self, leds)
        self.stopping = Event()
        self.fill_color = fill_color
        self.fill_animation = FillLedAnimation(leds, fill_color, reverse)

    def start(self, timeout=None, one_shot=False):
        self.stopping.clear()
        end_time = time() + timeout if timeout else None

        while not self.stopping.is_set():
            self.fill_animation.start()
            self.fill_animation.fill_color = Color.BLACK
            self.fill_animation.start()
            self.fill_animation.fill_color = self.fill_color
            if one_shot:
                self.stopping.set()
            elif end_time and time() > end_time:
                self.stopping.set()

    def stop(self):
        self.stopping.set()


class BounceLedAnimation(LedAnimation):
    def __init__(self, leds: AbstractLed, fill_color: Color,
                 reverse: bool = False):
        """
        Fill effect in the requested color, followed by reversed fill effect
        in black. Animation repeats until timing out or being stopped.
        LEDs are turned off after animation.
        @param leds: LED object to interact with
        @param fill_color: Color to fill LEDs
        @param reverse: If true, fill in reverse order
        """
        LedAnimation.__init__(self, leds)
        self.stopping = Event()
        self.fill_color = fill_color
        self.fill_animation = FillLedAnimation(leds, fill_color, reverse)

    def start(self, timeout=None, one_shot=False):
        self.stopping.clear()
        end_time = time() + timeout if timeout else None

        while not self.stopping.is_set():
            self.fill_animation.start()
            self.fill_animation.reverse = not self.fill_animation.reverse
            self.fill_animation.fill_color = Color.BLACK
            self.fill_animation.start()
            self.fill_animation.reverse = not self.fill_animation.reverse
            self.fill_animation.fill_color = self.fill_color
            if one_shot:
                self.stopping.set()
            elif end_time and time() > end_time:
                self.stopping.set()

    def stop(self):
        self.stopping.set()


class BlinkLedAnimation(LedAnimation):
    def __init__(self, leds: AbstractLed, color: Color,
                 num_blinks: int = 2, repeat: bool = False):
        """
        Blink LEDs in the requested color, for the requested number of blinks.
        If repeating, pause and repeat the effect until timeout or stop event.
        @param leds: LED object to interact with
        @param color: Color to blink LEDs
        @param num_blinks: Number of times to blink LEDs
        @param repeat: If true, repeat animation until timeout or stopped
        """
        LedAnimation.__init__(self, leds)
        self.stopping = Event()
        self.color = color
        self.num_blinks = num_blinks
        self.repeat = repeat

    def start(self, timeout=None, one_shot=False):
        self.stopping.clear()
        end_time = time() + timeout if timeout else None

        self.leds.fill(Color.BLACK.as_rgb_tuple())
        sleep(0.5)
        while not self.stopping.is_set():
            for i in range(self.num_blinks):
                self.leds.fill(self.color.as_rgb_tuple())
                sleep(0.25)
                self.leds.fill(Color.BLACK.as_rgb_tuple())
                sleep(0.5)
            if one_shot:
                self.stopping.set()
            elif self.repeat:
                sleep(2)
            else:
                self.stopping.set()
            if end_time and time() > end_time:
                self.stopping.set()

    def stop(self):
        self.stopping.set()


animations = {
    'breathe': BreatheLedAnimation,
    'chase': ChaseLedAnimation,
    'fill': FillLedAnimation,
    'refill': RefillLedAnimation,
    'bounce': BounceLedAnimation,
    'blink': BlinkLedAnimation
}
