from speech2text.engines import STT
import json
import requests


class YandexSTT(STT):
    """
        Yandex SpeechKit STT
        To use create service account with role 'editor' in your cloud folder,
        create API key for account and add it to local mycroft.conf file.
        The STT config will look like this:

        "stt": {
            "module": "yandex",
            "yandex": {
                "lang": "en-US",
                "credential": {
                    "api_key": "YOUR_API_KEY"
                }
            }
        }
    """
    def __init__(self, config=None):
        super(YandexSTT, self).__init__(config)
        self.api_key = self.credential.get("api_key")
        if self.api_key is None:
            raise ValueError("API key for Yandex STT is not defined")

    def execute(self, audio, language=None):
        self.lang = language or self.lang
        if self.lang not in ["en-US", "ru-RU", "tr-TR"]:
            raise ValueError(
                "Unsupported language '{}' for Yandex STT".format(self.lang))

        # Select sample rate based on source sample rate
        # and supported sample rate list
        supported_sample_rates = [8000, 16000, 48000]
        sample_rate = audio.sample_rate
        if sample_rate not in supported_sample_rates:
            for supported_sample_rate in supported_sample_rates:
                if audio.sample_rate < supported_sample_rate:
                    sample_rate = supported_sample_rate
                    break
            if sample_rate not in supported_sample_rates:
                sample_rate = supported_sample_rates[-1]

        raw_data = audio.get_raw_data(convert_rate=sample_rate,
                                      convert_width=2)

        # Based on https://cloud.yandex.com/docs/speechkit/stt#request
        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        headers = {"Authorization": "Api-Key {}".format(self.api_key)}
        params = "&".join([
            "lang={}".format(self.lang),
            "format=lpcm",
            "sampleRateHertz={}".format(sample_rate)
        ])

        response = requests.post(url + "?" + params, headers=headers,
                                 data=raw_data)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result.get("error_code") is None:
                return result.get("result")
        elif response.status_code == 401:  # Unauthorized
            raise Exception("Invalid API key for Yandex STT")
        else:
            raise Exception(
                "Request to Yandex STT failed: code: {}, body: {}".format(
                    response.status_code, response.text))
