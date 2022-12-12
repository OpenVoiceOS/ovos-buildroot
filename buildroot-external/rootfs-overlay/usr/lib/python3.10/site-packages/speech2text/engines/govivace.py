from speech2text.engines import TokenSTT
from speech2text.log import LOG
import requests


class GoVivaceSTT(TokenSTT):
    def __init__(self, config=None):
        super(GoVivaceSTT, self).__init__(config)
        self.url = self.config.get(
            "uri", "https://services.govivace.com:49149/telephony")

        if not self.lang.startswith("en") and not self.lang.startswith("es"):
            LOG.error("GoVivace STT only supports english and spanish")
            raise NotImplementedError

    def execute(self, audio, language=None):
        url = self.url + "?key=" + \
              self.token + "&action=find&format=8K_PCM16&validation_string="
        response = requests.put(url, data=audio.get_wav_data(
            convert_rate=8000))
        return response.json()["result"]["hypotheses"][0]["transcript"]
