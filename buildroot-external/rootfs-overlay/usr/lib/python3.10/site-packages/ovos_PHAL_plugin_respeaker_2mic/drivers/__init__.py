from ovos_PHAL_plugin_respeaker_2mic.drivers import button
from ovos_PHAL_plugin_respeaker_2mic.drivers.pixels import Pixels

# GPIO definitions (BCM)
_GPIO_BUTTON = 17
_GPIO_LED = 25

# Global variables. They are lazily initialized.
_voicehat_button = None
_voicehat_led = None


def get_button():
    global _voicehat_button
    if not _voicehat_button:
        _voicehat_button = button.Button(channel=_GPIO_BUTTON)
    return _voicehat_button


def get_led():
    global _voicehat_led
    if not _voicehat_led:
        _voicehat_led = Pixels()
    return _voicehat_led
