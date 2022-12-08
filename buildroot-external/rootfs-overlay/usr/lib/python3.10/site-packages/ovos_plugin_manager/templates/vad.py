from ovos_config import Configuration


class VADEngine:
    def __init__(self, config=None, sample_rate=None):
        self.config_core = Configuration()
        self.config = config or {}
        self.sample_rate = sample_rate or \
                           self.config_core.get("listener", {}).get("sample_rate", 16000)

    def is_silence(self, chunk):
        # return True or False
        return False

