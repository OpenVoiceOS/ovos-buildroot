# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from abc import ABCMeta, abstractmethod
from speech_recognition import Recognizer
from queue import Queue
from threading import Thread


class STT(metaclass=ABCMeta):
    """ STT Base class, all  STT backends derives from this one. """
    def __init__(self, config=None):
        self.config = config or {}
        self.lang = self.init_language(self.config)
        self.credential = self.config.get("credential") or {}
        self.recognizer = Recognizer()
        self.can_stream = False

    @staticmethod
    def init_language(config):
        lang = config.get("lang", "en-US")
        langs = lang.split("-")
        if len(langs) == 2:
            return langs[0].lower() + "-" + langs[1].upper()
        return lang

    @abstractmethod
    def execute(self, audio, language=None):
        pass


class TokenSTT(STT, metaclass=ABCMeta):
    def __init__(self, config=None):
        super(TokenSTT, self).__init__(config)
        self.token = self.credential.get("token")


class BasicSTT(STT, metaclass=ABCMeta):

    def __init__(self, config=None):
        super(BasicSTT, self).__init__(config)
        self.username = str(self.credential.get("username"))
        self.password = str(self.credential.get("password"))


class KeySTT(STT, metaclass=ABCMeta):

    def __init__(self, config=None):
        super(KeySTT, self).__init__(config)
        self.id = str(self.credential.get("client_id"))
        self.key = str(self.credential.get("client_key"))


class StreamThread(Thread, metaclass=ABCMeta):
    """
        ABC class to be used with StreamingSTT class implementations.
    """

    def __init__(self, queue, language):
        super().__init__()
        self.language = language
        self.queue = queue
        self.text = None

    def _get_data(self):
        while True:
            d = self.queue.get()
            if d is None:
                break
            yield d
            self.queue.task_done()

    def run(self):
        return self.handle_audio_stream(self._get_data(), self.language)

    @abstractmethod
    def handle_audio_stream(self, audio, language):
        pass

    def finalize(self):
        """
        Engines can perform final operations before stream closes here
        usually modify self.text
        """
        pass


class StreamingSTT(STT, metaclass=ABCMeta):
    """
        ABC class for threaded streaming STT implemenations.
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.stream = None
        self.can_stream = True

    def stream_start(self, language=None):
        self.stream_stop()
        language = language or self.lang
        self.queue = Queue()
        self.stream = self.create_streaming_thread()
        self.stream.start()

    def stream_data(self, data):
        self.queue.put(data)

    def stream_stop(self):
        if self.stream is not None:
            self.queue.put(None)
            self.stream.finalize()
            self.stream.join()

            text = self.stream.text

            self.stream = None
            self.queue = None
            return text
        return None

    def execute(self, audio, language=None):
        return self.stream_stop()

    @abstractmethod
    def create_streaming_thread(self):
        pass








