from os.path import join, isfile, expanduser, dirname
from ovos_plugin_manager.templates.hotwords import HotWordEngine
from ovos_utils.log import LOG
import requests
from os import makedirs
from precise_lite_runner import PreciseLiteListener, ReadWriteStream
from ovos_utils.xdg_utils import xdg_data_home


class PreciseLiteHotwordPlugin(HotWordEngine):
    """Precise is the default wake word engine for Mycroft.
    This is the community developed TfLite version of that engine
    """

    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super().__init__(key_phrase, config, lang)
        self.expected_duration = self.config.get("expected_duration") or 3
        self.has_found = False
        self.stream = ReadWriteStream()
        self.chunk_size = 2048
        self.trigger_level = self.config.get('trigger_level', 3)
        self.sensitivity = self.config.get('sensitivity', 0.5)

        default_model = "https://github.com/OpenVoiceOS/precise-lite-models/raw/master/wakewords/en/hey_mycroft.tflite"
        model = self.config.get('model', default_model)
        if model and model.startswith("http"):
            model = self.download_model(model)

        if not model or not isfile(expanduser(model)):
            raise ValueError("Model not found")

        self.precise_model = expanduser(model)

        self.runner = PreciseLiteListener(model=self.precise_model,
                                          stream=self.stream,
                                          chunk_size=self.chunk_size,
                                          trigger_level=self.trigger_level,
                                          sensitivity=self.sensitivity,
                                          on_activation=self.on_activation,
                                          )
        self.runner.start()

    @staticmethod
    def download_model(url):
        name = url.split("/")[-1].split(".")[0] + ".tflite"
        folder = join(xdg_data_home(), "precise-lite")
        model_path = join(folder, name)
        if not isfile(model_path):
            LOG.info("Downloading model for precise-lite:")
            LOG.info(url)
            content = requests.get(url).content
            makedirs(folder, exist_ok=True)
            with open(model_path, "wb") as f:
                f.write(content)
            LOG.info(f"Model downloaded to {model_path}")

        return model_path

    def on_activation(self):
        self.has_found = True

    def update(self, chunk):
        self.stream.write(chunk)

    def found_wake_word(self, frame_data):
        if self.has_found:
            self.has_found = False
            return True
        return False

    def stop(self):
        if self.runner:
            self.runner.stop()
