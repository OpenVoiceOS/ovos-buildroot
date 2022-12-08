import subprocess
import re
import collections


class PulseAudio:
    volume_re = re.compile('^set-sink-volume ([^ ]+) (.*)')
    mute_re = re.compile('^set-sink-mute ([^ ]+) ((?:yes)|(?:no))')

    def __init__(self):
        self._mute = collections.OrderedDict()
        self._volume = collections.OrderedDict()
        self.update()

    def normalize_sinks(self):
        self.unmute_all()
        volume = self.get_volume()
        self.set_all_volumes(volume)

    def update(self):
        proc = subprocess.Popen(['pacmd', 'dump'], stdout=subprocess.PIPE)

        for line in proc.stdout:
            line = line.decode("utf-8")
            volume_match = PulseAudio.volume_re.match(line)
            mute_match = PulseAudio.mute_re.match(line)

            if volume_match:
                self._volume[volume_match.group(1)] = int(
                    volume_match.group(2), 16)
            elif mute_match:
                self._mute[mute_match.group(1)] = mute_match.group(
                    2).lower() == "yes"

    def _vol_to_percent(self, vol):
        max_vol = 65536
        percent = vol * 100 / max_vol
        return percent

    def _percent_to_vol(self, percent):
        max_vol = 65536
        vol = percent * max_vol / 100
        return vol

    def get_volume_percent(self, sink=None):
        vol = self.get_sink_volume(sink)
        return self._vol_to_percent(vol)

    def get_mute(self, sink=None):
        if not sink:
            sink = list(self._mute.keys())[0]

        return self._mute[sink]

    def get_volume(self, sink=None):
        return self.get_sink_volume(sink)

    def get_sink_volume(self, sink=None):
        if not sink:
            sink = list(self._volume.keys())[0]

        return self._volume[sink]

    def set_mute(self, mute, sink=None):
        if not sink:
            sink = list(self._mute.keys())[0]

        subprocess.Popen(
            ['pacmd', 'set-sink-mute', sink, 'yes' if mute else 'no'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._mute[sink] = mute

    def set_volume(self, volume, sink=None):
        self.set_sink_volume(volume, sink)

    def set_volume_percent(self, volume, sink=None):
        self.set_sink_volume(self._percent_to_vol(volume), sink)

    def set_sink_volume(self, volume, sink=None):
        if not sink:
            sink = list(self._volume.keys())[0]
        volume = int(volume)
        subprocess.Popen(['pacmd', 'set-sink-volume', sink, hex(volume)],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._volume[sink] = volume

    def mute_all(self):
        for sink in self.list_sinks():
            self.set_mute(True, sink)

    def unmute_all(self):
        for sink in self.list_sinks():
            self.set_mute(False, sink)

    def set_all_volumes(self, volume):
        self.set_all_sink_volumes(volume)

    def get_all_volumes(self):
        return self.get_all_sink_volumes()

    def set_all_volumes_percent(self, percent):
        volume = self._percent_to_vol(percent)
        self.set_all_sink_volumes(volume)

    def get_all_volumes_percent(self):
        return [self._vol_to_percent(volume) for volume in
                self.get_all_sink_volumes()]

    def set_all_sink_volumes(self, volume):
        for sink in self.list_sinks():
            self.set_volume(volume, sink)

    def get_all_sink_volumes(self):
        volumes = []
        for sink in self.list_sinks():
            volumes.append(self.get_volume(sink))
        return volumes

    def list_sinks(self):
        proc = subprocess.Popen(['pacmd', 'list-sinks'],
                                stdout=subprocess.PIPE)
        sinks = []
        for line in proc.stdout:
            line = line.decode("utf-8").strip()
            if line.startswith("name: <"):
                sink = line.replace("name: <", "")[:-1]
                sinks.append(sink)
        return sinks

    def list_sources(self):
        proc = subprocess.Popen(['pacmd', 'list-sources'],
                                stdout=subprocess.PIPE)
        sinks = []
        for line in proc.stdout:
            line = line.decode("utf-8").strip()
            if line.startswith("name: <"):
                sink = line.replace("name: <", "")[:-1]
                sinks.append(sink)
        return sinks

    def increase_volume(self, percent):
        volume = self.get_volume_percent()
        volume += percent
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.set_all_volumes_percent(volume)

    def decrease_volume(self, percent):
        volume = self.get_volume_percent()
        volume -= percent
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100
        self.set_all_volumes_percent(volume)


if __name__ == "__main__":
    p = PulseAudio()
    print(p.list_sources())