from queue import Queue
from uuid import uuid4

import requests
from ovos_plugin_manager.stt import STT
from ovos_plugin_manager.stt import StreamingSTT, StreamThread


class OVOSHTTPServerSTT(STT):
    """STT interface for the OVOS-HTTP-STT-Server"""

    def __init__(self, config=None):
        super().__init__(config)
        self.url = self.config.get("url") or "https://stt.strongthany.cc/stt"

    def execute(self, audio, language=None):
        self.response = requests.post(self.url, data=audio.get_wav_data(),
                                      headers={"Content-Type": "audio/wav"},
                                      params={"session_id": language or self.lang})
        return self.response.text if self.response else None


class OVOSHTTPStreamServerStreamThread(StreamThread):
    def __init__(self, queue, language, url="https://stt.strongthany.cc/stream"):
        super().__init__(queue, language)
        self.url = url
        self.session = requests.Session()

    def reset_model(self, session_id=None):
        self.session_id = session_id or str(uuid4())
        # reset the model for this session
        response = self.session.post(f"{self.url}/start",
                                     params={"lang": self.language,
                                             "uuid": self.session_id})

    def handle_audio_stream(self, audio, language):
        lang = language or self.language
        response = self.session.post(f"{self.url}/audio",
                                     params={"lang": lang,
                                             "uuid": self.session_id},
                                     data=audio, stream=True)
        self.text = response.json()["transcript"]
        return self.text

    def finalize(self):
        """ return final transcription """
        try:
            response = self.session.post(f"{self.url}/end",
                                         params={"lang": self.language,
                                                 "uuid": self.session_id})
            self.text = response.json()["transcript"] or self.text
        except:
            pass
        return self.text


class OVOSHTTPStreamServerSTT(StreamingSTT):
    """Streaming STT interface for the OVOS-HTTP-STT-Server"""

    def create_streaming_thread(self):
        url = self.config.get('url') or "https://stt.strongthany.cc/stream"
        self.queue = Queue()

        stream = OVOSHTTPStreamServerStreamThread(self.queue, self.lang, url)
        stream.reset_model()
        return stream


# will list the public instances of google STT proxies as valid configs
# but thats not the main intended usage of this plugin


# taken from https://stackoverflow.com/questions/14257598/what-are-language-codes-in-chromes-implementation-of-the-html5-speech-recogniti/14302134#14302134
_lang = {
    "Afrikaans": [
        ["South Africa", "af-ZA"]
    ],
    "Arabic": [
        ["Algeria", "ar-DZ"],
        ["Bahrain", "ar-BH"],
        ["Egypt", "ar-EG"],
        ["Israel", "ar-IL"],
        ["Iraq", "ar-IQ"],
        ["Jordan", "ar-JO"],
        ["Kuwait", "ar-KW"],
        ["Lebanon", "ar-LB"],
        ["Morocco", "ar-MA"],
        ["Oman", "ar-OM"],
        ["Palestinian Territory", "ar-PS"],
        ["Qatar", "ar-QA"],
        ["Saudi Arabia", "ar-SA"],
        ["Tunisia", "ar-TN"],
        ["UAE", "ar-AE"]
    ],
    "Basque": [
        ["Spain", "eu-ES"]
    ],
    "Bulgarian": [
        ["Bulgaria", "bg-BG"]
    ],
    "Catalan": [
        ["Spain", "ca-ES"]
    ],
    "Chinese Mandarin": [
        ["China (Simp.)", "cmn-Hans-CN"],
        ["Hong Kong SAR (Trad.)", "cmn-Hans-HK"],
        ["Taiwan (Trad.)", "cmn-Hant-TW"]
    ],
    "Chinese Cantonese": [
        ["Hong Kong", "yue-Hant-HK"]
    ],
    "Croatian": [
        ["Croatia", "hr_HR"]
    ],
    "Czech": [
        ["Czech Republic", "cs-CZ"]
    ],
    "Danish": [
        ["Denmark", "da-DK"]
    ],
    "English": [
        ["Australia", "en-AU"],
        ["Canada", "en-CA"],
        ["India", "en-IN"],
        ["Ireland", "en-IE"],
        ["New Zealand", "en-NZ"],
        ["Philippines", "en-PH"],
        ["South Africa", "en-ZA"],
        ["United Kingdom", "en-GB"],
        ["United States", "en-US"]
    ],
    "Farsi": [
        ["Iran", "fa-IR"]
    ],
    "French": [
        ["France", "fr-FR"]
    ],
    "Filipino": [
        ["Philippines", "fil-PH"]
    ],
    "Galician": [
        ["Spain", "gl-ES"]
    ],
    "German": [
        ["Germany", "de-DE"]
    ],
    "Greek": [
        ["Greece", "el-GR"]
    ],
    "Finnish": [
        ["Finland", "fi-FI"]
    ],
    "Hebrew": [
        ["Israel", "he-IL"]
    ],
    "Hindi": [
        ["India", "hi-IN"]
    ],
    "Hungarian": [
        ["Hungary", "hu-HU"]
    ],
    "Indonesian": [
        ["Indonesia", "id-ID"]
    ],
    "Icelandic": [
        ["Iceland", "is-IS"]
    ],
    "Italian": [
        ["Italy", "it-IT"],
        ["Switzerland", "it-CH"]
    ],
    "Japanese": [
        ["Japan", "ja-JP"]
    ],
    "Korean": [
        ["Korea", "ko-KR"]
    ],
    "Lithuanian": [
        ["Lithuania", "lt-LT"]
    ],
    "Malaysian": [
        ["Malaysia", "ms-MY"]
    ],
    "Dutch": [
        ["Netherlands", "nl-NL"]
    ],
    "Norwegian": [
        ["Norway", "nb-NO"]
    ],
    "Polish": [
        ["Poland", "pl-PL"]
    ],
    "Portuguese": [
        ["Brazil", "pt-BR"],
        ["Portugal", "pt-PT"]
    ],
    "Romanian": [
        ["Romania", "ro-RO"]
    ],
    "Russian": [
        ["Russia", "ru-RU"]
    ],
    "Serbian": [
        ["Serbia", "sr-RS"]
    ],
    "Slovak": [
        ["Slovakia", "sk-SK"]
    ],
    "Slovenian": [
        ["Slovenia", "sl-SI"]
    ],
    "Spanish": [
        ["Argentina", "es-AR"],
        ["Bolivia", "es-BO"],
        ["Chile", "es-CL"],
        ["Colombia", "es-CO"],
        ["Costa Rica", "es-CR"],
        ["Dominican Republic", "es-DO"],
        ["Ecuador", "es-EC"],
        ["El Salvador", "es-SV"],
        ["Guatemala", "es-GT"],
        ["Honduras", "es-HN"],
        ["México", "es-MX"],
        ["Nicaragua", "es-NI"],
        ["Panamá", "es-PA"],
        ["Paraguay", "es-PY"],
        ["Perú", "es-PE"],
        ["Puerto Rico", "es-PR"],
        ["Spain", "es-ES"],
        ["Uruguay", "es-UY"],
        ["United States", "es-US"],
        ["Venezuela", "es-VE"]
    ],
    "Swedish": [
        ["Sweden", "sv-SE"]
    ],
    "Thai": [
        ["Thailand", "th-TH"]
    ],
    "Turkish": [
        ["Turkey", "tr-TR"]
    ],
    "Ukrainian": [
        ["Ukraine", "uk-UA"]
    ],
    "Vietnamese": [
        ["Viet Nam", "vi-VN"]
    ],
    "Zulu": [
        ["South Africa", "zu-ZA"]
    ]
}

OVOSHTTPServerSTTConfig = {}

for lang, data in _lang.items():
    for region, code in data:
        OVOSHTTPServerSTTConfig[code] = [
            {"lang": code,
             "url": "https://stt.openvoiceos.com",
             "meta": {
                 "priority": 30,
                 "display_name": f"OVOS Google Proxy {lang} ({region})",
                 "offline": False}
             },
            {"lang": code,
             "url": "https://stt.strongthany.cc",
             "meta": {
                 "priority": 80,
                 "display_name": f"Strongthany Google Proxy {lang} ({region})",
                 "offline": False}
             }
        ]
