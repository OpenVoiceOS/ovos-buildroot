try:
    import alsaaudio
except ImportError:
    alsaaudio = None
from ovos_utils.log import LOG


class AlsaControl:
    _mixer = None

    def __init__(self, control=None):
        if alsaaudio is None:
            LOG.error("pyalsaaudio not installed")
            LOG.info("Run pip install pyalsaaudio==0.8.2")
            raise ImportError
        if control is None:
            control = alsaaudio.mixers()[0]
        self.get_mixer(control)

    @property
    def mixer(self):
        return self._mixer

    def get_mixer(self, control="Master"):
        if self._mixer is None:
            try:
                mixer = alsaaudio.Mixer(control)
            except Exception as e:
                try:
                    mixer = alsaaudio.Mixer(control)
                except Exception as e:
                    try:
                        if control != "Master":
                            LOG.warning("could not allocate requested mixer, "
                                        "falling back to 'Master'")
                            mixer = alsaaudio.Mixer("Master")
                        else:
                            raise
                    except Exception as e:
                        LOG.error("Couldn't allocate mixer")
                        LOG.exception(e)
                        raise
            self._mixer = mixer
        return self.mixer

    def increase_volume(self, percent):
        volume = self.get_volume()
        if isinstance(volume, list):
            volume = volume[0]
        volume += percent
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.mixer.setvolume(int(volume))

    def decrease_volume(self, percent):
        volume = self.get_volume()
        if isinstance(volume, list):
            volume = volume[0]
        volume -= percent
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.mixer.setvolume(int(volume))

    def set_volume_percent(self, percent):
        self.set_volume(percent)

    def set_volume(self, volume):
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.mixer.setvolume(int(volume))

    def volume_range(self):
        return self.mixer.getrange()

    def is_muted(self):
        return bool(self.mixer.getmute()[0])

    def mute(self):
        return self.mixer.setmute(1)

    def unmute(self):
        return self.mixer.setmute(0)

    def toggle_mute(self):
        if self.is_muted():
            self.unmute()
        else:
            self.mute()

    def get_volume(self):
        return self.mixer.getvolume()[0]

    def get_volume_percent(self):
        return self.get_volume()


if __name__ == "__main__":
    from time import sleep
    a = AlsaControl()
    a.set_volume(100)
    sleep(2)
    print(a.is_muted())
    a.mute()
    print(a.is_muted())
    sleep(2)
    a.unmute()
    print(a.is_muted())
    print(a.get_volume())
    sleep(2)
    a.set_volume(50)
    print(a.get_volume())
    sleep(2)
    a.set_volume(70)
    print(a.get_volume())
    sleep(2)
    a.set_volume(10)
    print(a.get_volume())
    sleep(2)
    a.set_volume(80)
    print(a.get_volume())
