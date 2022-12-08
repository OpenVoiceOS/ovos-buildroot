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

import json
from os import path, remove
from json_database import JsonStorage
from uuid import uuid4


class DashboardHandler:
    def __init__(self, file_system_path, skill_folder_path):
        self.dashboard_model = JsonStorage(
            file_system_path + "/dashboard.json")
        self.dashboard_collection = self.dashboard_model.get("collection", [])
        self.skill_folder_path = skill_folder_path

        if len(self.dashboard_collection) == 0:
            self.prepend_inital_dashboard_cards()

    def prepend_inital_dashboard_cards(self):
        """
        Prepends initial cards to the dashboard
        """
        with open(self.skill_folder_path + "/initialcards.json", "r") as f:
            initial_cards = json.load(f)
        for card in initial_cards.get("collection", []):
            url = self.skill_folder_path + "/" + card['url']
            card["url"] = url
            self.add_item(card)

    def add_item(self, item):
        """
        Adds an item to the dashboard
        """
        if item not in self.dashboard_collection:
            item["id"] = str(uuid4())
            self.dashboard_collection.append(item)
            self.dashboard_model["collection"] = self.dashboard_collection
            self.dashboard_model.store()

    def remove_item(self, item_id):
        """
        Removes an item from the dashboard
        """
        print("Removing item in dashboard handler: " + item_id)
        try:
            self.dashboard_collection = [
                item for item in self.dashboard_collection if item["id"] != item_id]
            self.dashboard_model["collection"] = self.dashboard_collection
            self.dashboard_model.store()
        except Exception as e:
            print("Error removing item from dashboard: " + str(e))

    def get_collection(self):
        """
        Returns the current dashboard cards
        """
        gridItemModel = []
        for item in self.dashboard_collection:
            cellHeight = 5
            cellWidth = 5

            if item.get("verticalSize", "").lower() == "short":
                cellHeight = 3
            elif item.get("verticalSize", "").lower() == "standard":
                cellHeight = 5
            elif item.get("verticalSize", "").lower() == "long":
                cellHeight = 10
            else:
                cellHeight = 5

            if item.get("horizontalSize", "").lower() == "standard":
                cellWidth = 5
            elif item.get("horizontalSize", "").lower() == "long":
                cellWidth = 10
            else:
                cellWidth = 5

            gridItem = {
                "id": item.get("id", ""),
                "url": item.get("url",  ""),
                "cellHeight": cellHeight,
                "cellWidth": cellWidth
            }
            gridItemModel.append(gridItem)

        return gridItemModel
