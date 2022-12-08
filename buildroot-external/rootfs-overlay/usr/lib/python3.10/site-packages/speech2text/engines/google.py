from speech2text.engines import STT, TokenSTT, StreamThread, StreamingSTT
import json
from queue import Queue


class GoogleSTT(TokenSTT):
    def execute(self, audio, language=None):
        self.lang = language or self.lang
        return self.recognizer.recognize_google(audio, self.token, self.lang)


class GoogleCloudSTT(STT):
    def __init__(self, config=None):
        super().__init__(config)
        self.json_credentials = json.dumps(self.credential.get("json"))

    def execute(self, audio, language=None):
        self.lang = language or self.lang
        return self.recognizer.recognize_google_cloud(audio,
                                                      self.json_credentials,
                                                      self.lang)


class GoogleStreamThread(StreamThread):
    def __init__(self, queue, lang, client, streaming_config):
        super().__init__(queue, lang)
        self.client = client
        self.streaming_config = streaming_config

    def handle_audio_stream(self, audio, language):
        req = (types.StreamingRecognizeRequest(audio_content=x) for x in audio)
        responses = self.client.streaming_recognize(self.streaming_config, req)
        for res in responses:
            if res.results and res.results[0].is_final:
                self.text = res.results[0].alternatives[0].transcript
        return self.text


class GoogleCloudStreamingSTT(StreamingSTT):
    """
        Streaming STT interface for Google Cloud Speech-To-Text
        To use pip install google-cloud-speech and add the
        Google API key to local mycroft.conf file. The STT config
        will look like this:

        "stt": {
            "module": "google_cloud_streaming",
            "google_cloud_streaming": {
                "credential": {
                    "json": {
                        # Paste Google API JSON here
        ...

    """

    def __init__(self, config=None):
        global SpeechClient, types, enums, Credentials
        from google.cloud.speech import SpeechClient, types, enums
        from google.oauth2.service_account import Credentials

        super(GoogleCloudStreamingSTT, self).__init__(config)
        credentials = Credentials.from_service_account_info(
            self.credential.get('json')
        )

        self.client = SpeechClient(credentials=credentials)
        recognition_config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.lang,
            model='command_and_search',
            max_alternatives=1,
        )
        self.streaming_config = types.StreamingRecognitionConfig(
            config=recognition_config,
            interim_results=True,
            single_utterance=True,
        )

    def create_streaming_thread(self):
        self.queue = Queue()
        return GoogleStreamThread(
            self.queue,
            self.lang,
            self.client,
            self.streaming_config
        )
