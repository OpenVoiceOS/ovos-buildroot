# Copyright 2021 Aditya Mehra <aix.m@outlook.com>.
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

import os
import json
from mycroft_bus_client import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_config.config import read_mycroft_config, update_mycroft_config
from ovos_utils.log import LOG


class ConfigurationProviderPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-configuration-provider", config=config)
        self.bus = bus
        self.settings_meta = {}
        self.build_settings_meta()
        
        self.bus.on("ovos.phal.configuration.provider.list.groups",
                    self.list_groups)
        self.bus.on("ovos.phal.configuration.provider.get",
                    self.get_settings_meta)
        self.bus.on("ovos.phal.configuration.provider.set",
                    self.set_settings_in_config)

    def build_settings_meta(self):
        readable_config = read_mycroft_config()
        misc = {}
        new_config = {}

        for key in readable_config:
            if type(readable_config[key]) is not dict:
                misc[key] = readable_config[key]
            if type(readable_config[key]) is dict:
                new_config[key] = readable_config[key]

        new_config["misc"] = misc

        settings_meta_list = []
        for key in new_config:
            group_meta = {}
            group_meta["group_name"] = key.lower()
            group_meta["group_label"] = key.capitalize().replace("_", " ")
            group_meta["group_sections"] = []

            general = {}
            general["section_name"] = f"{key}_general"
            general["section_label"] = "General Configuration"
            general["section_fields"] = []
            general["section_description"] = "Configure the general settings of this module"

            subsections = []

            for subkey in new_config[key]:
                field = self.generate_field(subkey, type(
                    new_config[key][subkey]), new_config[key][subkey], group_name=key)

                if field[1] == "field":
                    general["section_fields"].append(field[0])
                elif field[1] == "obj":
                    subsections.append(field[0])
                    if field[2] is not None:
                        for sub_nested_section in field[2]:
                            if sub_nested_section is not None:
                                if len(sub_nested_section["section_fields"]) > 0:
                                    group_meta["group_sections"].append(
                                        sub_nested_section)

            if len(general["section_fields"]) > 0:
                group_meta["group_sections"].append(general)
            group_meta["group_sections"].extend(subsections)

            for section in group_meta["group_sections"]:
                if len(section["section_fields"]) == 0:
                    group_meta["group_sections"].remove(section)

            settings_meta_list.append(group_meta)

        self.settings_meta["settings"] = settings_meta_list

        # For Debug Write File To Disk
        with open("/tmp/settings_meta.json", "w") as f:
            f.write(json.dumps(self.settings_meta))

    def generate_section(self, section_name, value, group_name):
        subsection = {}
        subsection["section_name"] = section_name
        subsection["section_label"] = section_name.capitalize().replace(
            "_", " ")
        subsection["section_fields"] = []
        subsection["section_description"] = self.populate_section_description(
            section_name, group_name)
        nested_sections = []
        for key in value:
            if type(value[key]) != dict:
                field = self.generate_field(
                    key, type(value[key]), value[key], group_name=group_name)
                subsection["section_fields"].append(field[0])
            else:
                sub_nested_sections = self.generate_section(
                    key, value[key], group_name=group_name)
                if type(sub_nested_sections) == list:
                    for sub_nested_section in sub_nested_sections:
                        if sub_nested_section is not None:
                            if type(sub_nested_section) == list:
                                for sub_nested_section_item in sub_nested_section:
                                    nested_sections.append(
                                        sub_nested_section_item)
                            elif type(sub_nested_section) == dict:
                                nested_sections.append(sub_nested_section)

                else:
                    nested_sections.append(sub_nested_sections)

        if len(nested_sections) > 0:
            return [subsection, nested_sections]
        else:
            return [subsection, None]

    def generate_field(self, key, type, value, group_name):
        type = type
        section_key = key
        if type is dict:
            type_str = "obj"
            generated_section_data = self.generate_section(
                section_key, value, group_name)
            generated_section = generated_section_data[0]
            if generated_section_data[1] is not None:
                nested_sections = generated_section_data[1]
                return [generated_section, type_str, nested_sections]
            else:
                return [generated_section, type_str, None]

        else:
            value = value
            field = {}
            field["field_name"] = key
            field["field_label"] = key.capitalize().replace("_", " ")
            field["field_type"] = type.__name__
            field["field_value"] = value
            field["field_description"] = self.populate_field_description(
                field["field_name"], group_name)

            type_str = "field"
            return [field, type_str]

    def populate_section_description(self, section_name, section_group):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/descriptions.json", "r") as f:
            description_json = json.load(f)
            descriptions = description_json["collection"]
            for description in descriptions:
                if description["type"] == "section":
                    if description["key"] == section_name and description["group"] == section_group:
                        return description["value"]
        return ""

    def populate_field_description(self, field_name, field_group):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/descriptions.json", "r") as f:
            description_json = json.load(f)
            descriptions = description_json["collection"]
            for description in descriptions:
                if description["type"] == "field":
                    if description["key"] == field_name and description["group"] == field_group:
                        return description["value"]
        return ""
    
    def list_groups(self, message=None):
        group_names = []
        for group in self.settings_meta["settings"]:
            group_names.append(group["group_name"])
    
        self.bus.emit(Message("ovos.phal.configuration.provider.list.groups.response", {"groups": group_names}))

    def get_settings_meta(self, message=None):
        group_request = message.data.get("group")
        LOG.info(f"Getting settings meta for section: {group_request}")

        for group in self.settings_meta["settings"]:
            if group["group_name"] == group_request:
                LOG.info(f"Found group: {group_request}")
                self.bus.emit(Message("ovos.phal.configuration.provider.get.response", {
                    "settingsMetaData": group, "groupName": group_request}))

    def update_settings_meta(self, group_request):
        self.settings_meta = {}
        self.build_settings_meta()
        for group in self.settings_meta["settings"]:
            if group["group_name"] == group_request:
                self.bus.emit(Message("ovos.phal.configuration.provider.get.response", {
                    "settingsMetaData": group, "groupName": group_request}))

    def find_and_update_config(self, key, config, old_config_value):
        for item in config:
            if item["field_name"] == key:
                return item["field_value"]
        else:
            return old_config_value

    def set_settings_in_config(self, message=None):
        group_name = message.data.get("group_name")
        configuration = message.data.get("configuration")
        mycroft_config = read_mycroft_config()

        misc = {}
        new_config = {}

        for key in mycroft_config:
            if type(mycroft_config[key]) is not dict:
                misc[key] = mycroft_config[key]
            if type(mycroft_config[key]) is dict:
                new_config[key] = mycroft_config[key]

        new_config["misc"] = misc

        if group_name != "misc":
            for key in new_config:
                if key == group_name:
                    for subkey in new_config[key]:
                        if type(new_config[key][subkey]) is dict:
                            for subkey2 in new_config[key][subkey]:
                                new_config[key][subkey][subkey2] = self.find_and_update_config(
                                    subkey2, configuration, new_config[key][subkey][subkey2])
                                if type(new_config[key][subkey][subkey2]) is dict:
                                    for subkey3 in new_config[key][subkey][subkey2]:
                                        new_config[key][subkey][subkey2][subkey3] = self.find_and_update_config(
                                            subkey3, configuration, new_config[key][subkey][subkey2][subkey3])
                        else:
                            new_config[key][subkey] = self.find_and_update_config(
                                subkey, configuration, new_config[key][subkey])

                    mycroft_config_group = {}
                    mycroft_config_group[key] = new_config[key]

                    update_mycroft_config(mycroft_config_group)

        elif group_name == "misc":
            for key in new_config:
                if key == group_name:
                    for subkey in new_config[key]:
                        new_config[key][subkey] = self.find_and_update_config(
                            subkey, configuration, new_config[key][subkey])

                        update_mycroft_config(new_config[key][subkey])
