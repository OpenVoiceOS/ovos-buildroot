from ovos_plugin_manager.tts import find_tts_plugins
from ovos_plugin_manager.stt import find_stt_plugins
from ovos_plugin_manager.wakewords import find_wake_word_plugins
from ovos_plugin_manager.audio import find_audio_service_plugins
from ovos_plugin_manager.utils import load_plugin, PluginTypes
from ovos_plugin_manager.installation import pip_install
from ovos_utils import camel_case_split
from ovos_utils.json_helper import merge_dict


class OpenVoiceOSPlugin:
    def __init__(self, data):
        self._data = data
        self._clazz = None
        self._plugtype = None

    @staticmethod
    def from_name(name):
        data = {"name": name}
        if name in find_stt_plugins():
            data["plugin_type"] = PluginTypes.STT
        elif name in find_tts_plugins():
            data["plugin_type"] = PluginTypes.TTS
        elif name in find_wake_word_plugins():
            data["plugin_type"] = PluginTypes.WAKEWORD
        elif name in find_audio_service_plugins():
            data["plugin_type"] = PluginTypes.AUDIO
        engine = load_plugin(name)
        if engine:
            data["class"] = engine.__name__
            data["description"] = engine.__doc__

        return OpenVoiceOSPlugin(data)

    @property
    def json(self):
        data = {
            "name": self.name,
            "package_name": self.package_name,
            "module_name": self.module_name,
            "human_name": self.human_name,
            "description": self.description,
            "plugin_type": self.plugin_type,
            "url": self.url,
            "is_installed": self.is_installed,
            "class": self.clazz
        }
        return merge_dict(data, self._data)

    @property
    def name(self):
        return self._data.get("name")

    @property
    def package_name(self):
        return self._data.get("package_name")

    @property
    def module_name(self):
        if self.is_installed:
            if not self._data.get("module_name"):
                self._data["module_name"] = self._clazz.__module__
            return self._clazz.__module__
        return self._data.get("module_name")

    @property
    def human_name(self):
        if not self._data.get("human_name") and self.clazz:
            self._data["human_name"] = camel_case_split(self.clazz.__name__)
        if not self._data.get("human_name") and self.package_name:
            self._data["human_name"] = self.package_name
        if not self._data.get("human_name") and self.name:
            self._data["human_name"] = camel_case_split(self.name)
        # normalize it
        if self._data.get("human_name"):
            self._data["human_name"] = self._data["human_name"]\
                .replace("-", " ").replace("_", " ").title()\
                .replace("Tts", "TTS").replace("Stt", "STT")
        return self._data.get("human_name")

    @property
    def description(self):
        if not self._data.get("description") and self.clazz:
            self._data["description"] = self.clazz.__doc__
        return self._data.get("description")

    @property
    def plugin_type(self):
        # check json data
        if not self._plugtype and self._data.get("plugin_type"):
            self._plugtype = self._data.get("plugin_type")
            if "tts" in self._plugtype.lower():
                self._plugtype = PluginTypes.TTS
            elif "stt" in self._plugtype.lower():
                self._plugtype = PluginTypes.STT
            elif "word" in self._plugtype.lower():
                self._plugtype = PluginTypes.WAKEWORD
            elif "audio" in self._plugtype.lower():
                self._plugtype = PluginTypes.AUDIO
            else:
                self._plugtype = None

        # check if installed
        if not self._plugtype and self.name:
            if self.name in find_stt_plugins():
                self._plugtype = PluginTypes.STT
            elif self.name in find_tts_plugins():
                self._plugtype = PluginTypes.TTS
            elif self.name in find_wake_word_plugins():
                self._plugtype = PluginTypes.WAKEWORD
            elif self.name in find_audio_service_plugins():
                self._plugtype = PluginTypes.AUDIO

        # parse name
        if not self._plugtype and self.name:
            if "tts" in self.name.lower():
                self._plugtype = PluginTypes.TTS
            elif "stt" in self.name.lower():
                self._plugtype = PluginTypes.STT
            elif "word" in self.name.lower():
                self._plugtype = PluginTypes.WAKEWORD
            elif "audio" in self.name.lower():
                self._plugtype = PluginTypes.AUDIO

        # parse description
        if not self._plugtype and self.description:
            if "tts" in self.description.lower():
                self._plugtype = PluginTypes.TTS
            elif "stt" in self.description.lower():
                self._plugtype = PluginTypes.STT
            elif "word" in self.description.lower():
                self._plugtype = PluginTypes.WAKEWORD
            elif "audio" in self.description.lower():
                self._plugtype = PluginTypes.AUDIO

        # parse package name
        if not self._plugtype and self.package_name:
            if "tts" in self.package_name.lower():
                self._plugtype = PluginTypes.TTS
            elif "stt" in self.package_name.lower():
                self._plugtype = PluginTypes.STT
            elif "word" in self.package_name.lower():
                self._plugtype = PluginTypes.WAKEWORD
            elif "audio" in self.package_name.lower():
                self._plugtype = PluginTypes.AUDIO

        # parse module name
        if not self._plugtype and self.module_name:
            if "tts" in self.module_name.lower():
                self._plugtype = PluginTypes.TTS
            elif "stt" in self.module_name.lower():
                self._plugtype = PluginTypes.STT
            elif "word" in self.module_name.lower():
                self._plugtype = PluginTypes.WAKEWORD
            elif "audio" in self.module_name.lower():
                self._plugtype = PluginTypes.AUDIO

        if not self._data.get("plugin_type"):
            self._data["plugin_type"] = self._plugtype
        return self._plugtype

    @property
    def url(self):
        return self._data.get("url")

    @property
    def is_installed(self):
        return self.clazz is not None

    @property
    def clazz(self):
        if not self._clazz and self.name:
            self._clazz = self.load()
        return self._clazz

    def load(self):
        return load_plugin(self.name, plug_type=self.plugin_type)

    def install(self):
        if self.package_name:
            return pip_install(self.package_name)
        if self.url and "github" in self.url:
            return pip_install("git+" + self.url)
        return False
