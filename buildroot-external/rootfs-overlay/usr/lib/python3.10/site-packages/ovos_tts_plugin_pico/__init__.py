import subprocess
import wave
from distutils.spawn import find_executable

from ovos_plugin_manager.templates.tts import TTS, TTSValidator


def get_voice_from_lang(lang):
    if lang.startswith("de"):
        return "de-DE"
    if lang.startswith("es"):
        return "es-ES"
    if lang.startswith("fr"):
        return "fr-FR"
    if lang.startswith("it"):
        return "it-IT"
    if lang.startswith("en"):
        if "gb" in lang.lower() or "uk" in lang.lower():
            return "en-GB"
        else:
            return "en-US"


class PicoTTS(TTS):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, audio_ext="wav",
                         validator=PicoTTSValidator(self))
        if not self.voice:
            self.voice = get_voice_from_lang(self.lang)

        # TODO support speed and pitch for nanotts
        self.nanotts = find_executable("nanotts")
        self.pico2wave = find_executable("pico2wave")
        self.picotts = find_executable("pico-tts")
        if not self.nanotts and not self.pico2wave and not self.picotts:
            raise RuntimeError("pico2wave/pico-tts executable not found")

    def get_nanotts(self, sentence, wav_file, voice):
        subprocess.call(
            [self.nanotts, '-v', voice, "-o", wav_file, sentence])
        return wav_file

    def get_pico2wave(self, sentence, wav_file, voice):
        subprocess.call(
            [self.pico2wave, '-l', voice, "-w", wav_file, sentence])
        return wav_file

    def get_picotts(self, sentence, wav_file, voice):
        # uncompressed PCM over stdout. PCM_U8
        # Pipe to aplay -q -f S16_LE -r 16 to listen to it, or redirect to a file
        p = subprocess.Popen([self.picotts, '-l', voice],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        pcmdata, _ = p.communicate(sentence.encode("utf-8"))

        with wave.open(wav_file, 'wb') as f:
            f.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
            f.writeframes(pcmdata)

        return wav_file

    def get_tts(self, sentence, wav_file, lang=None):
        if lang:
            voice = get_voice_from_lang(lang) or self.voice
        else:
            voice = self.voice
        if self.nanotts:
            wav_file = self.get_nanotts(sentence, wav_file, voice)
        elif self.pico2wave:
            wav_file = self.get_pico2wave(sentence, wav_file, voice)
        else:
            wav_file = self.get_picotts(sentence, wav_file, voice)
        return wav_file, None

    @property
    def available_languages(self) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set(PicoTTSPluginConfig.keys())


class PicoTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(PicoTTSValidator, self).__init__(tts)

    def validate_lang(self):
        voices = ['de-DE', 'en-GB', 'en-US', 'es-ES', 'fr-FR', 'it-IT']
        lang = self.tts.lang.split("-")[0].lower().strip()
        supported = [v.split("-")[0].lower().strip() for v in voices]
        if lang not in supported:
            raise Exception('PicoTTS only supports ' + str(voices))

    def validate_connection(self):
        if not find_executable("pico2wave") and \
                not find_executable("pico-tts") and \
                not find_executable("nanotts"):
            raise Exception(
                'PicoTTS is not installed. Run: '
                '\nsudo apt-get install libttspico0\n'
                'sudo apt-get install  libttspico-utils')

    def get_tts_class(self):
        return PicoTTS


PicoTTSPluginConfig = {
    lang: [
        {"lang": lang, "meta": {"gender": "female", "display_name": f"Pico ({lang})", "offline": True, "priority": 60}}
    ] for lang in ["de", "es", "fr", "en", "it"]
}

if __name__ == "__main__":
    e = PicoTTS()

    ssml = """Hello world"""
    e.get_tts(ssml, "pico.wav")
