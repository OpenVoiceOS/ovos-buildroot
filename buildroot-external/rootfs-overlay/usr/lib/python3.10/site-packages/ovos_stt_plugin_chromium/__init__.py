import json
import logging

import requests
from ovos_plugin_manager.templates.stt import STT
from ovos_utils.log import LOG

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

ChromiumSTTConfig = {}

for lang, data in _lang.items():
    for region, code in data:
        ChromiumSTTConfig[code] = [
            {"lang": code,
             "pfilter": False,
             "meta": {
                 "priority": 40,
                 "display_name": f"{lang} ({region})",
                 "offline": False}
             }
        ]


class ChromiumSTT(STT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pfilter = self.config.get("pfilter", False)
        self.lang = self.config.get("lang") or self.lang

        # no keys issued since at least march 9 2016
        # http://web.archive.org/web/20160309230031/http://www.chromium.org/developers/how-tos/api-keys
        # key scrapped from commit linked bellow, dated Jun 8, 2014
        # https://github.com/Uberi/speech_recognition/commit/633c2cf54466a748d1db6ad0715c8cbdb27dbb09
        # let's hope it just keeps on working!
        default_key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"

        self.key = self.config.get("key") or default_key
        self.debug = self.config.get("debug", False)
        if not self.debug:
            log = logging.getLogger("urllib3.connectionpool")
            log.setLevel("INFO")

    def execute(self, audio, language=None):
        flac_data = audio.get_flac_data(
            convert_rate=None if audio.sample_rate >= 8000 else 8000,
            # audio samples must be at least 8 kHz
            convert_width=2  # audio samples must be 16-bit
        )

        params = {
            "client": "chromium",
            "lang": language or self.lang,
            "key": self.key,
            "pFilter": int(self.pfilter)
        }
        sample_rate = str(audio.sample_rate)
        headers = {"Content-Type": "audio/x-flac; rate=" + sample_rate}
        url = "http://www.google.com/speech-api/v2/recognize"
        r = requests.post(url, headers=headers, data=flac_data, params=params)

        # weirdly this returns something like
        """
        {"result":[]}
        {"result":[{"alternative":[{"transcript":"Hello world","confidence":0.83848035},{"transcript":"hello hello"},{"transcript":"Hello"},{"transcript":"Hello old"},{"transcript":"Hello howdy"}],"final":true}],"result_index":0}
        """

        result = r.text.split("\n")[1]
        data = json.loads(result)["result"]
        if len(data) == 0:
            return ""
        data = data[0]["alternative"]
        if self.debug:
            LOG.debug("transcriptions:" + str(data))
        if len(data) == 0:
            return ""

        # we arbitrarily choose the first hypothesis by default.
        # results seem to be ordered by confidence
        best_hypothesis = data[0]["transcript"]

        # if confidence is provided return highest conf
        candidates = [alt for alt in data if alt.get("confidence")]
        if self.debug:
            LOG.debug("confidences: " + str(candidates))

        if len(candidates):
            best = max(candidates, key=lambda alt: alt["confidence"])
            best_hypothesis = best["transcript"]
            if self.debug:
                LOG.debug("best confidence: " + best_hypothesis)
        return best_hypothesis
