from ovos_plugin_manager.phal import PHALPlugin
from os.path import join, dirname
from ovos_utils.sound import play_audio
from ovos_utils.sound.alsa import AlsaControl
from mycroft_bus_client import Message
from json_database import JsonConfigXDG


class AlsaVolumeControlPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-alsa", config=config)
        self.settings = JsonConfigXDG(self.name, subfolder="OpenVoiceOS")
        self.alsa = AlsaControl()
        self.volume_sound = join(dirname(__file__), "blop-mark-diangelo.wav")
        self.bus.on("mycroft.volume.get", self.handle_volume_request)
        self.bus.on("mycroft.volume.set", self.handle_volume_change)
        self.bus.on("mycroft.volume.increase", self.handle_volume_increase)
        self.bus.on("mycroft.volume.decrease", self.handle_volume_decrease)
        self.bus.on("mycroft.volume.set.gui", self.handle_volume_change_gui)
        self.bus.on("mycroft.volume.mute", self.handle_mute_request)
        self.bus.on("mycroft.volume.unmute", self.handle_unmute_request)
        self.bus.on("mycroft.volume.mute.toggle", self.handle_mute_toggle_request)

        # A silent method to get the volume without invoking the shell osd
        # Needed as gui will always refresh and request it
        # When sliding panel opens to refresh volume value data
        self.bus.on("mycroft.volume.get.sliding.panel", self.handle_volume_request)

        if self.settings.get("first_boot", True):
            self.set_volume(50)
            self.settings["first_boot"] = False
            self.settings.store()

    def get_volume(self):
        return self.alsa.get_volume_percent()

    def set_volume(self, percent=None, set_by_gui=False):
        volume = int(percent)
        volume = min(100, volume)
        volume = max(0, volume)
        self.alsa.set_volume_percent(volume)
        play_audio(self.volume_sound)
        # report change to GUI
        if not set_by_gui:
            percent = volume / 100
            self.handle_volume_request(
                Message("mycroft.volume.get", {"percent": percent}))

    def increase_volume(self, volume_change=None):
        if not volume_change:
            volume_change = 15
        self.alsa.increase_volume(volume_change)
        play_audio(self.volume_sound)
        self.handle_volume_request(Message("mycroft.volume.get"))

    def decrease_volume(self, volume_change=None):
        if not volume_change:
            volume_change = -15
        if volume_change > 0:
            volume_change = 0 - volume_change
        self.alsa.increase_volume(volume_change)
        play_audio(self.volume_sound)
        self.handle_volume_request(Message("mycroft.volume.get"))

    def handle_mute_request(self, message):
        self.log.info("User muted audio.")
        self.alsa.mute()
        self.bus.emit(Message("mycroft.volume.get").response({"percent": 0}))

    def handle_unmute_request(self, message):
        self.log.info("User unmuted audio.")
        self.alsa.unmute()
        volume = self.alsa.get_volume_percent()
        self.bus.emit(Message("mycroft.volume.get").response({"percent": volume / 100}))

    def handle_mute_toggle_request(self, message):
        self.alsa.toggle_mute()
        muted = self.alsa.is_muted()
        self.log.info(f"User toggled mute. Result: {'muted' if muted else 'unmuted'}")
        self.bus.emit(Message("mycroft.volume.get").response(
            {"percent": 0 if muted else (self.alsa.get_volume_percent() / 100)}))

    def handle_volume_request(self, message):
        percent = self.get_volume() / 100
        self.bus.emit(message.response({"percent": percent}))

    def handle_volume_change(self, message):
        percent = message.data["percent"] * 100
        self.set_volume(percent)

    def handle_volume_increase(self, message):
        percent = message.data.get("percent", .10) * 100
        self.increase_volume(percent)

    def handle_volume_decrease(self, message):
        percent = message.data.get("percent", -.10) * 100
        self.decrease_volume(percent)

    def handle_volume_change_gui(self, message):
        percent = message.data["percent"] * 100
        self.set_volume(percent, set_by_gui=True)

    def shutdown(self):
        self.bus.remove("mycroft.volume.get", self.handle_volume_request)
        self.bus.remove("mycroft.volume.set", self.handle_volume_change)
        self.bus.remove("mycroft.volume.increase", self.handle_volume_increase)
        self.bus.remove("mycroft.volume.decrease", self.handle_volume_decrease)
        self.bus.remove("mycroft.volume.set.gui", self.handle_volume_change_gui)
        self.bus.remove("mycroft.volume.mute", self.handle_mute_request)
        self.bus.remove("mycroft.volume.unmute", self.handle_unmute_request)
        self.bus.remove("mycroft.volume.mute.toggle", self.handle_mute_toggle_request)
        super().shutdown()
