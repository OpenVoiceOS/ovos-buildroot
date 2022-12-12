# Copyright 2022, OpenVoiceOS.
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

import datetime
from mycroft_bus_client import Message


class CardGenerator:
    def __init__(self, file_system_path, bus, skill_folder_path):
        self.bus = bus
        self.storage_area = file_system_path
        self.skill_folder_path = skill_folder_path

    def generate(self, data):
        current_date_time = datetime.datetime.now().strftime("%Y%H%M%S")

        with open(self.skill_folder_path + "/ui/templates/CardTemplate.qml", "r") as f:
            template_file = f.read()
            template_file = template_file.replace(
                "action-holder", data["action"])
            template_file = template_file.replace(
                "header-holder", data["header"])
            template_file = template_file.replace(
                "text-holder", data["description"])
            template_file = template_file.replace(
                "box-icon-holder", data["icon"])
            template_file = template_file.replace(
                "icon-color-holder", data["iconColor"])

            with open(self.storage_area + "/CustomCard" + current_date_time + ".qml", "w") as f:
                f.write(template_file)
                f.close()

        self.card = {
            "url": "file://" + self.storage_area + "/CustomCard" + current_date_time + ".qml",
            "verticalSize": "standard",
            "horizontalSize": "standard"
        }
        self.bus.emit(
            Message("ovos.homescreen.dashboard.add.card", {"card": self.card}))
