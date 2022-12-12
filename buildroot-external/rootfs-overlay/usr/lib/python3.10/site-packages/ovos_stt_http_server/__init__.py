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
from tempfile import NamedTemporaryFile
from time import sleep

from flask import Flask, request
from ovos_plugin_manager.stt import load_stt_plugin
from ovos_utils.log import LOG
from speech_recognition import Recognizer, AudioFile, AudioData


class ModelContainer:
    def __init__(self, plugin, config=None):
        self.plugin = load_stt_plugin(plugin)
        if not self.plugin:
            raise ValueError(f"Failed to load STT: {plugin}")
        self.engines = {}
        self.data = {}
        self.config = config or {}

    def get_engine(self, session_id):
        if session_id not in self.engines:
            self.load_engine(session_id)
        return self.engines[session_id]

    def load_engine(self, session_id, config=None):
        config = config or self.config
        self.engines[session_id] = self.plugin(config=config)

    def unload_engine(self, session_id):
        if session_id in self.engines:
            self.engines.pop(session_id)
        if session_id in self.data:
            self.data.pop(session_id)

    def process_audio(self, audio, lang, session_id=None):
        session_id = session_id or lang  # shared model for non-streaming stt
        engine = self.get_engine(session_id)
        if audio or engine.can_stream:
            return engine.execute(audio, language=lang) or ""
        return ""

    def stream_start(self, session_id):
        engine = self.get_engine(session_id)
        if engine.can_stream:
            engine.stream_start()

    def stream_data(self, audio, session_id):
        engine = self.get_engine(session_id)
        if engine.can_stream:
            # streaming plugin in server + streaming plugin in core
            return engine.stream_data(audio)
        else:
            # non streaming plugin in server + streaming plugin in core
            if session_id not in self.data:
                self.data[session_id] = b""
            self.data[session_id] += audio
        return ""

    def stream_stop(self, session_id):
        engine = self.get_engine(session_id)
        if engine.can_stream:
            transcript = engine.stream_stop()
        else:
            audio = AudioData(self.data[session_id],
                              sample_rate=16000, sample_width=2)
            transcript = engine.execute(audio)
        self.unload_engine(session_id)
        return transcript or ""


def bytes2audiodata(data):
    recognizer = Recognizer()
    with NamedTemporaryFile() as fp:
        fp.write(data)
        with AudioFile(fp.name) as source:
            audio = recognizer.record(source)
    return audio


def create_app(stt_plugin):
    app = Flask(__name__)
    model = ModelContainer(stt_plugin)

    @app.route("/stt", methods=['POST'])
    def get_stt():
        lang = str(request.args.get("lang", "en-us")).lower()
        audio = bytes2audiodata(request.data)
        return model.process_audio(audio, lang)

    @app.route("/stream/start", methods=['POST'])
    def stream_start():
        lang = str(request.args.get("lang", "en-us")).lower()
        uuid = str(request.args.get("uuid") or lang)
        model.load_engine(uuid, {"lang": lang})
        model.stream_start(uuid)
        return {"status": "ok", "uuid": uuid, "lang": lang}

    @app.route("/stream/audio", methods=['POST'])
    def stream():
        audio = request.data
        lang = str(request.args.get("lang", "en-us")).lower()
        uuid = str(request.args.get("uuid") or lang)
        transcript = model.stream_data(audio, uuid)
        return {"status": "ok", "uuid": uuid,
                "lang": lang, "transcript": transcript}

    @app.route("/stream/end", methods=['POST'])
    def stream_end():
        lang = str(request.args.get("lang", "en-us")).lower()
        uuid = str(request.args.get("uuid") or lang)
        # model.wait_until_done(uuid)
        transcript = model.stream_stop(uuid)
        LOG.info(transcript)
        return {"status": "ok", "uuid": uuid,
                "lang": lang, "transcript": transcript}

    return app


def start_stt_server(engine, port=9666, host="0.0.0.0"):
    app = create_app(engine)
    app.run(port=port, use_reloader=False, host=host)
    return app
