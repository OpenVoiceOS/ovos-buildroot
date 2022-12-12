"""
this module is meant to enable usage of mycroft plugins inside and outside
mycroft, importing from here will make things work as planned in mycroft,
but if outside mycroft things will still work

The main use case is for plugins to be used across different projects
"""
from ovos_plugin_manager.templates.audio import AudioBackend, RemoteAudioBackend
from ovos_plugin_manager.templates.tts import TTS, TTSValidator
from ovos_plugin_manager.templates.stt import STT, StreamingSTT, StreamThread, GoogleJsonSTT, KeySTT, TokenSTT, BasicSTT
from ovos_plugin_manager.templates.hotwords import HotWordEngine
