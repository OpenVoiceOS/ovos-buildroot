from ovos_backend_client.api import STTApi
from ovos_plugin_manager.templates.stt import STT

# taken from https://stackoverflow.com/questions/14257598/what-are-language-codes-in-chromes-implementation-of-the-html5-speech-recogniti/14302134#14302134
_langs = {
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

SeleneSTTConfig = {}

for lang, data in _langs.items():
    for region, code in data:
        SeleneSTTConfig[code] = [
            {"lang": code,
             "meta": {
                 "priority": 60,
                 "display_name": f"{lang} ({region})",
                 "offline": False}
             }
        ]


class SeleneSTT(STT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        server_cfg = self.config_core.get("server", {})
        url = self.config.get("host") \
              or server_cfg.get("url") \
              or "https://api.mycroft.ai"
        version = self.config.get("version") \
                  or server_cfg.get("version") \
                  or "v1"
        identity_file = self.config.get("identity_file")  # if None default file is used
        self.api = STTApi(url, version, identity_file)

    def execute(self, audio, language=None):
        lang = language or self.lang
        try:
            return self.api.stt(audio.get_flac_data(convert_rate=16000), lang, 1)[0]
        except Exception:
            return self.api.stt(audio.get_flac_data(), lang, 1)[0]
