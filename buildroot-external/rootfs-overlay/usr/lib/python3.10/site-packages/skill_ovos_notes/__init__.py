# Copyright 2022 OpenVoiceOS.
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

import os
import base64
import datetime
from mycroft.skills import MycroftSkill, intent_file_handler
from json_database import JsonStorage
from mycroft.messagebus.message import Message


class OVOSNotesSkill(MycroftSkill):

    def __init__(self):
        super().__init__(name="OVOSNotesSkill")
        self.notes_dir = None
        self.all_notes_db = None
        self.all_notes_in_db = None
        self.current_note = None
        self.current_mode = None  # "1: personal note" or "2: all notes"

    def initialize(self):
        self.notes_dir = self.file_system.path + "/"
        self.all_notes_db = JsonStorage(self.notes_dir + 'all_notes.json')
        if "all_notes" in self.all_notes_db:
            self.all_notes_in_db = self.all_notes_db["all_notes"]
        else:
            self.all_notes_in_db = []

        self.gui.register_handler(
            'ovos.notes.skill.edit.current.note', self.handle_edit_note)
        self.gui.register_handler(
            'ovos.notes.skill.remove.current.note', self.handle_remove_current_note)
        self.gui.register_handler(
            'ovos.notes.skill.reset.current.note', self.handle_reset_current_note)
        self.gui.register_handler(
            "ovos.notes.skill.open.selected.note", self.handle_open_selected_note)
        self.gui.register_handler(
            "ovos.notes.skill.remove.selected.note", self.handle_remove_selected_note)
        self.gui.register_handler(
            "ovos.notes.skill.add.note", self.take_personal_note)
        self.gui.register_handler(
            "ovos.notes.skill.release.skill", self.handle_release_skill)
        self.gui.register_handler(
            "ovos.notes.skill.change.notes.mode", 
            self.update_selected_mode_on_page_change)
        self.gui.register_handler(
            "ovos.notes.skill.show.all.notes",
            self.show_all_notes)

    # generate an incremental note number
    def generate_note_number(self):
        if len(self.all_notes_in_db) == 0:
            return 1
        else:
            return self.all_notes_in_db[-1]['note_number'] + 1

    @intent_file_handler('take_personal_note.intent')
    def take_personal_note(self, message):
        self.current_note = None
        self.current_mode = 1
        self.gui["personalNoteText"] = " "
        note_number = self.generate_note_number()
        self.gui['noteNumber'] = note_number
        self.gui.show_page('PersonalNote.qml')
        note = self.get_response('request_note_response', num_retries=1)
        
        if note is None:
            self.speak("Sorry, I didn't hear anything.")
            
        else:
            note_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
            note_file_path = self.notes_dir + note_file_name
            with open(note_file_path, 'w') as f:
                f.write(base64.b64encode(note.encode('utf-8')).decode('utf-8'))
            self.all_notes_in_db.append({
                'note_number': note_number,
                'file_name': note_file_name,
                'file_path': note_file_path
            })
            self.all_notes_db["all_notes"] = self.all_notes_in_db
            self.all_notes_db.store()
            self.current_note = note_file_name

            # show the note in the GUI
            self.gui["personalNoteText"] = note

            # speak the note if no gui is available
            if not self.gui.connected:
                self.speak_dialog("taken_note_reply")
                self.handle_read_last_note({})

    @intent_file_handler('show_all_notes.intent')
    def show_all_notes(self, message):
        build_model = []
        build_model_obj = {}
        all_note_local_representation = self.all_notes_db["all_notes"]
        for note in all_note_local_representation:
            with open(note['file_path'], 'r') as f:
                note_text = base64.b64decode(f.read()).decode('utf-8')
            build_model.append({
                    'note_number': note['note_number'],
                    'file_name': note['file_name'],
                    'note_text': note_text
                })

        sort_on = "note_number"
        decorated = [(dict_[sort_on], dict_)
                     for dict_ in build_model]
        decorated.sort(reverse=True)
        sorted_model = [dict_ for (key, dict_) in decorated]
        build_model_obj["allNotes"] = sorted_model
        self.current_mode = 2
        self.gui.show_page('AllNotes.qml')

        self.gui["allNotesModel"] = build_model_obj

    @intent_file_handler('edit_current_note.intent')
    def handle_edit_note(self, message):
        # handle editing the current note
        if self.current_note:
            note = self.get_response('request_note_response', num_retries=1)
            note_file_path = self.notes_dir + self.current_note
            with open(note_file_path, 'w') as f:
                f.write(base64.b64encode(note.encode('utf-8')).decode('utf-8'))

            # find the note in the all_notes_in_db and update it
            for note_obj in self.all_notes_in_db:
                if note_obj['file_name'] == self.current_note:
                    note_obj['note_text'] = note
                    break

            self.all_notes_db["all_notes"] = self.all_notes_in_db
            self.all_notes_db.store()

        self.gui["personalNoteText"] = note
        self.update_notes_model_on_page_change()

    @intent_file_handler('remove_current_note.intent')
    def handle_remove_current_note(self, message):
        # handle removing the current note
        if self.current_note:
            note_file_path = self.notes_dir + self.current_note
            os.remove(note_file_path)
            # find the note in the all_notes_in_db and remove it
            for note_obj in self.all_notes_in_db:
                if note_obj['file_name'] == self.current_note:
                    self.all_notes_in_db.remove(note_obj)
                    break

            self.all_notes_db["all_notes"] = self.all_notes_in_db
            self.all_notes_db.store()
            self.handle_reset_current_note({})

    @intent_file_handler('delete_note_by_number.intent')
    def delete_note_by_number(self, message):
        get_num = message.data.get('number')
        for note_obj in self.all_notes_in_db:
            if note_obj['note_number'] == int(get_num):
                self.handle_remove_selected_note(
                    Message({'file_name': note_obj['file_name']}))

    @intent_file_handler('open_note_by_number.intent')
    def open_note_by_number(self, message):
        get_num = message.data.get('number')
        for note_obj in self.all_notes_in_db:
            if note_obj['note_number'] == int(get_num):
                self.handle_open_selected_note(
                    Message({'file_name': note_obj['file_name']}))

    @intent_file_handler("read_all_notes.intent")
    def handle_read_all_notes(self, message):
        all_note_local_representation = self.all_notes_db["all_notes"]
        for note in all_note_local_representation:
            with open(note['file_path'], 'r') as f:
                note_text = base64.b64decode(f.read()).decode('utf-8')
            speakable_text = "Note number " + \
                str(note['note_number']) + " say's : " + note_text
            self.speak(speakable_text)

    @intent_file_handler("read_x_number_of_notes_from_top.intent")
    def handle_read_x_number_of_notes_from_top(self, message):
        # handle reading x number of notes from the all notes view
        all_note_local_representation = self.all_notes_db["all_notes"]
        number_of_notes_to_read = message.data.get('number', 1)
        if number_of_notes_to_read.split()[0].isdigit():
            extract_num = number_of_notes_to_read.split(" ")[0]
        else:
            extract_num = number_of_notes_to_read

        if int(extract_num) > len(all_note_local_representation):
            extract_num = len(all_note_local_representation)

        if extract_num:
            for number_of_notes_read in range(0, int(extract_num)):
                note = all_note_local_representation[number_of_notes_read]
                with open(note['file_path'], 'r') as f:
                    note_text = base64.b64decode(f.read()).decode('utf-8')
                speakable_text = "Note number " + \
                    str(note['note_number']) + " say's : " + note_text
                self.speak(speakable_text)

    @intent_file_handler("read_x_number_of_notes_from_bottom.intent")
    def handle_read_x_number_of_notes_from_bottom(self, message):
        # handle reading x number of notes
        # from the all notes view from the bottom
        all_note_local_representation = self.all_notes_db["all_notes"]

        sort_on = "note_number"
        decorated = [(dict_[sort_on], dict_)
                     for dict_ in all_note_local_representation]
        decorated.sort(reverse=True)
        sorted_model = [dict_ for (key, dict_) in decorated]

        number_of_notes_to_read = message.data.get('number', 1)
        if number_of_notes_to_read.split()[0].isdigit():
            extract_num = number_of_notes_to_read.split(" ")[0]
        else:
            extract_num = number_of_notes_to_read

        if int(extract_num) > len(all_note_local_representation):
            extract_num = len(all_note_local_representation)

        if extract_num:
            for number_of_notes_read in range(0, int(extract_num)):
                note = sorted_model[number_of_notes_read]
                with open(note['file_path'], 'r') as f:
                    note_text = base64.b64decode(f.read()).decode('utf-8')
                speakable_text = "Note number " + \
                    str(note['note_number']) + " say's : " + note_text
                self.speak(speakable_text)

    @intent_file_handler("read_last_note.intent")
    def handle_read_last_note(self, message):
        # handle reading the last note from the all notes view
        all_note_local_representation = self.all_notes_db["all_notes"]
        note = all_note_local_representation[-1]
        with open(note['file_path'], 'r') as f:
            note_text = base64.b64decode(f.read()).decode('utf-8')
        speakable_text = "Note number " + \
            str(note['note_number']) + " say's : " + note_text
        self.speak(speakable_text)

    @intent_file_handler("read_note_by_number.intent")
    def handle_read_note_by_number(self, message):
        get_num = message.data.get('number')
        for note_obj in self.all_notes_in_db:
            if note_obj['note_number'] == int(get_num):
                with open(note_obj['file_path'], 'r') as f:
                    note_text = base64.b64decode(f.read()).decode('utf-8')
                speakable_text = "Note number " + \
                    str(note_obj['note_number']) + " say's : " + note_text
                self.speak(speakable_text)

    def handle_reset_current_note(self, message):
        self.current_note = None
        self.current_mode = None
        self.gui["personalNoteText"] = " "
        self.update_notes_model_on_page_change()
        self.gui.remove_page('PersonalNote.qml')
        self.bus.emit(Message("metadata", {"type": "stop"}))
           
    def handle_reset_all_notes_view(self, message):
        self.gui.remove_page('AllNotes.qml')
        self.current_mode = None
        self.bus.emit(Message("metadata", {"type": "stop"}))

    def handle_open_selected_note(self, message):
        # handle opening a selected note from the all notes view
        # with file_name
        file_name = message.data["file_name"]
        file_path = self.notes_dir + file_name
        with open(file_path, 'r') as f:
            note_text = base64.b64decode(f.read()).decode('utf-8')
        self.gui["personalNoteText"] = note_text
        self.current_note = file_name
        self.gui.show_page('PersonalNote.qml')

    def handle_remove_selected_note(self, message):
        # handle removing a selected note from the all notes view
        # with file_name
        file_name = message.data["file_name"]
        file_path = self.notes_dir + file_name
        # if file exists remove it
        if os.path.isfile(file_path):
            os.remove(file_path)
            # find the note in the all_notes_in_db and remove it
            for note_obj in self.all_notes_in_db:
                if note_obj['file_name'] == file_name:
                    self.all_notes_in_db.remove(note_obj)
                    break

            self.all_notes_db["all_notes"] = self.all_notes_in_db
            self.all_notes_db.store()

            # Update the all notes view
            self.show_all_notes({})
            
    def update_selected_mode_on_page_change(self, message):
        mode = message.data["mode"]
        self.current_mode = mode
        
    def update_notes_model_on_page_change(self):
        build_model = []
        build_model_obj = {}
        all_note_local_representation = self.all_notes_db["all_notes"]
        for note in all_note_local_representation:
            with open(note['file_path'], 'r') as f:
                note_text = base64.b64decode(f.read()).decode('utf-8')
            build_model.append({
                    'note_number': note['note_number'],
                    'file_name': note['file_name'],
                    'note_text': note_text
                })

        sort_on = "note_number"
        decorated = [(dict_[sort_on], dict_)
                     for dict_ in build_model]
        decorated.sort(reverse=True)
        sorted_model = [dict_ for (key, dict_) in decorated]
        build_model_obj["allNotes"] = sorted_model
        self.gui["allNotesModel"] = build_model_obj

    def handle_release_skill(self, message):
        self.stop()
        self.gui.release()

    def stop(self):
        self.bus.emit(Message("metadata", {"type": "stop"}))
        if self.current_mode == 1:
            self.handle_reset_current_note({})
        elif self.current_mode == 2:
            self.handle_reset_all_notes_view({})
        pass


def create_skill():
    return OVOSNotesSkill()
