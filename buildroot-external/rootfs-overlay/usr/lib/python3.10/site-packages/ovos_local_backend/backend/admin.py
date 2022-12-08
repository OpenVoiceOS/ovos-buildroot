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
import time
from ovos_local_backend.backend import API_VERSION
from ovos_local_backend.utils import nice_json
from ovos_local_backend.database.settings import DeviceDatabase
from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.backend.decorators import noindex, requires_admin
from flask import request
from ovos_local_backend.utils import generate_code
from ovos_local_backend.utils.geolocate import get_request_location


def get_admin_routes(app):
    @app.route("/" + API_VERSION + "/admin/<uuid>/pair", methods=['GET'])
    @requires_admin
    @noindex
    def pair_device(uuid):
        code = generate_code()
        token = f"{code}:{uuid}"
        # add device to db
        location = get_request_location()
        with DeviceDatabase() as db:
            db.add_device(uuid, token, location=location)

        device = {"uuid": uuid,
                  "expires_at": time.time() + 99999999999999,
                  "accessToken": token,
                  "refreshToken": token}
        return nice_json(device)

    @app.route("/" + API_VERSION + "/admin/<uuid>/device", methods=['PUT'])
    @requires_admin
    @noindex
    def set_device(uuid):
        data = request.json
        with DeviceDatabase() as db:
            device = db.get_device(uuid)
            if not device:
                return {"error": "unknown device"}
            if "name" in data:
                device.name = data["name"]
            if "opt_in" in data:
                device.opt_in = data["opt_in"]
            if "device_location" in data:
                device.device_location = data["device_location"]
            if "email" in data:
                device.email = data["email"]
            if "isolated_skills" in data:
                device.isolated_skills = data["isolated_skills"]
            if "lang" in data:
                device.lang = data["lang"]
            db.update_device(device)
            return nice_json(device.serialize())

    @app.route("/" + API_VERSION + "/admin/<uuid>/location", methods=['PUT'])
    @requires_admin
    @noindex
    def set_location(uuid):
        with DeviceDatabase() as db:
            device = db.get_device(uuid)
            if not device:
                return {"error": "unknown device"}
            device.location = request.json
            db.update_device(device)
            return nice_json(device.serialize())

    @app.route("/" + API_VERSION + "/admin/<uuid>/prefs", methods=['PUT'])
    @requires_admin
    @noindex
    def set_prefs(uuid):
        data = request.json
        with DeviceDatabase() as db:
            device = db.get_device(uuid)
            if not device:
                return {"error": "unknown device"}
            if "time_format" in data:
                device.time_format = data["time_format"]
            if "date_format" in data:
                device.date_format = data["date_format"]
            if "system_unit" in data:
                device.system_unit = data["system_unit"]
            if "lang" in data:
                device.lang = data["lang"]
            if "tts_module" in data:
                device.default_tts = data["tts_module"]
                if "tts_config" in data:
                    device.default_tts_cfg = data["tts_config"]
                elif data["tts_module"] in CONFIGURATION["tts_configs"]:
                    device.default_tts_cfg = CONFIGURATION["tts_configs"][data["tts_module"]]
                else:
                    device.default_tts_cfg = {}
            if "wake_word" in data:
                device.default_ww = data["wake_word"]
                if "ww_config" in data:
                    device.default_ww_cfg = data["ww_config"]
                elif data["ww_module"] in CONFIGURATION["ww_configs"]:
                    device.default_ww_cfg = CONFIGURATION["ww_configs"][data["ww_module"]]
                else:
                    device.default_ww_cfg = {}
            db.update_device(device)
            return nice_json(device.serialize())

    return app
