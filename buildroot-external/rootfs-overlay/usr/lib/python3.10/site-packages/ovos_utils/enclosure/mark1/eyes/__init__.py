from ovos_utils.enclosure.mark1 import Mark1EnclosureAPI
from ovos_utils.messagebus import get_mycroft_bus
from ovos_utils.colors import Color
from ovos_utils import rotate_list
from time import sleep


class EyePixel:
    def __init__(self, index, api, color=None):
        self.index = index
        self.api = api
        self.color = color or Color()

    @property
    def rgb(self):
        return self.color.rgb255

    def sync_color(self):
        r, g, b = self.api.get_eyes_pixel_color(self.index)
        color = Color.from_rgb(r, g, b)
        self.change_color(color)

    def update_color(self):
        self.change_color(self.color)

    def change_color(self, name):
        if isinstance(name, str):
            self.color = Color.from_name(name)
        elif isinstance(name, Color):
            self.color = name
        else:
            raise ValueError("not a Color object")
        r, g, b = self.rgb
        self.api.eyes_setpixel(self.index, r, g, b)

    def set_saturation(self, value):
        self.color.set_saturation(value)
        self.update_color()

    def set_luminance(self, value):
        self.color.set_luminance(value)
        self.update_color()

    def set_hue(self, value):
        self.color.set_hue(value)
        self.update_color()

    def __repr__(self):
        return "Pixel_" + str(self.index) + ":" + self.color.color_description


class Eye(list):
    def __init__(self, pixel_range, bus=None, color=None):
        super().__init__()
        self.bus = bus or get_mycroft_bus()
        self.api = Mark1EnclosureAPI(self.bus)
        for idx in range(pixel_range[0], pixel_range[1]):
            pixel = EyePixel(idx, self.api)
            self.append(pixel)
        self.color = Color()
        if color:
            self.change_color(color)
        else:
            self.sync_color()

    def sync_color(self):
        for p in self:
            p.sync_color()
            sleep(0.05)

    def update_color(self):
        for p in self:
            p.update_color()
            sleep(0.05)

    def change_color(self, name):
        if isinstance(name, str):
            self.color = Color.from_name(name)
        elif isinstance(name, Color):
            self.color = name
        else:
            raise ValueError("not a Color object")
        for led in self:
            led.change_color(self.color)
            # writer bugs out if messages sent too fast
            sleep(0.05)

    def saturation_spin(self, speed=0.05):
        values = []
        for idx, pixel in enumerate(self):
            sat = 0.09 * idx
            pixel.set_saturation(sat)
            values.append(sat)
            sleep(speed)

        while True:
            values = rotate_list(values, -1)
            for idx, value in enumerate(values):
                self[idx].set_saturation(value)
                sleep(speed)

    def luminance_spin(self, speed=0.05):
        values = []
        for idx, pixel in enumerate(self):
            sat = 0.05 * idx
            pixel.set_luminance(sat)
            values.append(sat)
            sleep(speed)

        while True:
            values = rotate_list(values, -1)
            for idx, value in enumerate(values):
                self[idx].set_luminance(value)
                sleep(speed)

    def hue_spin(self, speed=0.05):
        values = []
        for idx, pixel in enumerate(self):
            sat = 0.083 * idx
            pixel.set_hue(sat)
            values.append(sat)
            sleep(speed)

        while True:
            values = rotate_list(values, -1)
            for idx, value in enumerate(values):
                self[idx].set_hue(value)
                sleep(speed)

    def set_hue(self, hue):
        for pixel in self:
            pixel.color.set_hue(hue)
            pixel.update_color()

    def set_luminance(self, value):
        for pixel in self:
            pixel.color.set_luminance(value)
        self.update_color()

    def set_saturation(self, value):
        for pixel in self:
            pixel.color.set_saturation(value)
        self.update_color()

    def on(self):
        self.set_luminance(1)

    def off(self):
        self.set_luminance(0)

    def blink_once(self):
        """
        Make the eye blink
        """
        raise NotImplementedError

    def blink(self, speed=0.5):
        """
        Make the right eye blink in a loop
        """
        while True:
            self.blink_once()
            sleep(speed)


class RightEye(Eye):
    def __init__(self, bus, color=None):
        super().__init__(bus=bus, pixel_range=(12, 24), color=color)

    def sync_color(self):
        pixels = self.api.get_eyes_color()[12:]
        for idx, (r, g, b) in enumerate(pixels):
            self[idx].color = Color.from_rgb(r, g, b)
        self.update_color()

    def blink_once(self):
        """
        Make the right eye blink
        """
        self.api.eyes_blink("r")


class LeftEye(Eye):
    def __init__(self, bus, color=None):
        super().__init__(bus=bus, pixel_range=(0, 12), color=color)

    def sync_color(self):
        pixels = self.api.get_eyes_color()[:12]
        for idx, (r, g, b) in enumerate(pixels):
            self[idx].color = Color.from_rgb(r, g, b)
        self.update_color()

    def blink_once(self):
        """
        Make the left eye blink
        """
        self.api.eyes_blink("l")


class Eyes(list):
    def __init__(self, bus=None, color=None):
        super().__init__()
        self.bus = bus or get_mycroft_bus()
        self.api = Mark1EnclosureAPI(self.bus)
        self.right = RightEye(self.bus)
        self.left = LeftEye(self.bus)
        self.color = Color()
        if color:
            self.change_color(color)
        else:
            self.sync_color()

    def __getitem__(self, item):
        assert isinstance(item, int)
        assert 0 <= item <= 23
        if item < 12:
            return self.left[item]
        return self.right[item - 12]

    def __setitem__(self, key, value):
        assert isinstance(key, int)
        assert 0 <= key <= 23
        if key < 12:
            self.left[key] = value
        self.right[key] = value

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return len(self.left) + len(self.right)

    def sync_color(self):
        """ updates internal color value to current color """
        pixels = self.api.get_eyes_color()
        for idx, (r, g, b) in enumerate(pixels):
            self[idx].color = Color.from_rgb(r, g, b)

    def update_color(self):
        """ updates arduino color to current pixels """
        for i in range(len(self) // 2):
            self.left[i].update_color()
            sleep(0.05)
            self.right[i].update_color()
            sleep(0.05)

    def change_color(self, name):
        """ changes color of both eyes """
        if isinstance(name, str):
            self.color = Color.from_name(name)
        elif isinstance(name, Color):
            self.color = name
        else:
            raise ValueError("not a Color object")
        r, g, b = self.color.rgb255
        self.api.eyes_color(r, g, b)
        for idx in range(len(self)):
            self[idx].color = self.color

    # animations
    def saturation_spin(self, speed=0.05):
        values = []
        for idx in range(len(self) // 2):
            sat = 0.09 * idx
            values.append(sat)
            self.left[idx].set_saturation(sat)
            sleep(0.03)
            self.right[idx].set_saturation(sat)

        while True:
            values = rotate_list(values, -1)
            for idx, value in enumerate(values):
                self.left[idx].set_saturation(value)
                sleep(0.03)
                self.right[idx].set_saturation(value)
                sleep(speed)

    def luminance_spin(self, speed=0.05):
        values = []
        for idx in range(len(self) // 2):
            sat = 0.05 * idx
            values.append(sat)
            self.left[idx].set_luminance(sat)
            sleep(0.03)
            self.right[idx].set_luminance(sat)

        while True:
            values = rotate_list(values, -1)
            for idx, value in enumerate(values):
                self.left[idx].set_luminance(value)
                sleep(0.03)
                self.right[idx].set_luminance(value)
                sleep(speed)

    def hue_spin(self, speed=0.05):
        values = []
        for idx in range(len(self) // 2):
            sat = 0.083 * idx
            values.append(sat)
            self.left[idx].set_hue(sat)
            sleep(0.03)
            self.right[idx].set_hue(sat)

        while True:
            values = rotate_list(values, -1)
            for idx, value in enumerate(values):
                for pixel in self:
                    print(pixel)
                self.left[idx].set_hue(value)
                sleep(0.03)
                self.right[idx].set_hue(value)
                sleep(speed)

    def flash(self, speed=0.2):
        while True:
            sleep(speed)
            self.on()
            sleep(speed)
            self.off()

    def rainbow_flash(self, speed=0.2):
        colors = ["red", "orange", "yellow", "green", "cyan", "blue",
                  "violet", "purple"]
        while True:
            for color in colors:
                sleep(speed)
                self.off()
                self.change_color(color)
                sleep(speed)
                self.on()

    def beacon(self, speed=0.1):
        values = [i + i for i in range(30)]
        while True:
            for value in values:
                self.set_brightness(value)
                sleep(speed)
            values.reverse()

    def rainbow_beacon(self, speed=0.1):
        values = [i + i for i in range(30)]
        values += reversed(values)
        colors = ["red", "orange", "yellow", "green", "cyan", "blue",
                  "violet", "purple"]
        self.set_brightness(0)
        while True:
            for color in colors:
                for value in values:
                    sleep(speed)
                    self.set_brightness(value)
                self.change_color(color)

    # Arduino API
    def set_hue(self, hue):
        self.right.set_hue(hue)
        sleep(0.05)
        self.left.set_hue(hue)

    def set_brightness(self, level):
        """
        Set the brightness of the eyes in the display.
        Args:
            level (int): 1-30, bigger numbers being brighter
        """
        self.api.eyes_brightness(level)

    def spin(self):
        self.api.eyes_spin()

    def timed_spin(self, length):
        self.api.eyes_timed_spin(length)

    def reset(self):
        self.api.eyes_reset()

    def fill_once(self, percent):
        """
        Use the eyes as a type of progress meter
        Args:
            percent (int): 0-49 fills the right eye, 50-100 also covers left
        """
        self.api.eyes_fill(percent)

    def look(self, side):
        """Make the eyes look to the given side
        Args:
            side (str): 'r' for right
                        'l' for left
                        'u' for up
                        'd' for down
                        'c' for crossed
        """
        self.api.eyes_look(side)

    def look_right(self):
        self.look("r")

    def look_left(self):
        self.look("l")

    def look_up(self):
        self.look("u")

    def look_down(self):
        self.look("d")

    def cross(self):
        self.look("c")

    def narrow(self):
        """Make the eyes look narrow, like a squint"""
        self.api.eyes_narrow()

    def on(self):
        """Illuminate or show the eyes."""
        self.api.eyes_on()

    def off(self):
        """Turn off or hide the eyes."""
        self.api.eyes_off()

    def blink_once(self, side="b"):
        """Make the eyes blink
        Args:
            side (str): 'r', 'l', or 'b' for 'right', 'left' or 'both'
        """
        self.api.eyes_blink(side)

    def blink_right_once(self):
        self.right.blink_once()

    def blink_left_once(self):
        self.left.blink_once()

    def blink(self, speed=0.5):
        """
        Make the eyes blink in a loop
        """
        while True:
            self.blink_once()
            sleep(speed)

    def blink_right(self, speed=0.5):
        """
        Make the right eye blink in a loop
        """
        self.right.blink(speed)

    def blink_left(self, speed=0.5):
        """
        Make the left eyes blink in a loop
        """
        self.left.blink(speed)

    def blink_alternate(self, speed=0.5):
        """
        Make the eyes blink in a loop
        """
        while True:
            self.blink_right_once()
            sleep(speed)
            self.blink_left_once()
            sleep(speed)

    def up_down(self, speed=0.8):
        """
        Make the eyes blink in a loop
        """
        while True:
            self.look_up()
            sleep(speed)
            self.look_down()
            sleep(speed)

    def left_right(self, speed=0.8):
        """
        Make the eyes blink in a loop
        """
        while True:
            self.look_left()
            sleep(speed)
            self.look_right()
            sleep(speed)

    def fill(self, speed=0.1):
        values = [i for i in range(101)]
        values += reversed(values)
        while True:
            for percent in values:
                self.fill_once(percent)
                sleep(speed)

    def rainbow_fill(self, speed=0.1):
        values = [i for i in range(101)]
        values += reversed(values)
        colors = ["red", "orange", "yellow", "green", "cyan", "blue",
                  "violet", "purple"]
        while True:
            for color in colors:
                for percent in values:
                    self.fill_once(percent)
                    sleep(speed)
                    if percent == 100:
                        self.change_color(color)



if __name__ == "__main__":
    bus = get_mycroft_bus("192.168.1.70")
    eyes = Eyes(bus)
    eyes.hue_spin()
