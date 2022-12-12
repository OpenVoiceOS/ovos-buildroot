import time
from os import makedirs
from os.path import join, isdir

from json_database import JsonDatabaseXDG

from ovos_local_backend.backend.decorators import requires_opt_in
from ovos_local_backend.configuration import CONFIGURATION


@requires_opt_in
def save_stt_recording(uuid, audio, utterance):
    if not isdir(join(CONFIGURATION["data_path"], "utterances")):
        makedirs(join(CONFIGURATION["data_path"], "utterances"))
    wav = audio.get_wav_data()
    path = join(CONFIGURATION["data_path"], "utterances",
                utterance + str(time.time()).replace(".", "") + ".wav")
    with open(path, "wb") as f:
        f.write(wav)
    with JsonUtteranceDatabase() as db:
        db.add_utterance(utterance, path, uuid)


class UtteranceRecording:
    def __init__(self, utterance_id, transcription, path, uuid="AnonDevice"):
        self.utterance_id = utterance_id
        self.transcription = transcription
        self.path = path
        self.uuid = uuid


class JsonUtteranceDatabase(JsonDatabaseXDG):
    def __init__(self):
        super().__init__("ovos_utterances")

    def add_utterance(self, transcription, path, uuid="AnonDevice"):
        utterance_id = self.total_utterances() + 1
        utterance = UtteranceRecording(utterance_id, transcription, path, uuid)
        self.add_item(utterance)

    def total_utterances(self):
        return len(self)

    def __enter__(self):
        """ Context handler """
        return self

    def __exit__(self, _type, value, traceback):
        """ Commits changes and Closes the session """
        try:
            self.commit()
        except Exception as e:
            print(e)
