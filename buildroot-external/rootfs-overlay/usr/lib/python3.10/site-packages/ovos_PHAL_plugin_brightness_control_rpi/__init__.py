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

import datetime
import subprocess
import threading
import time
from os.path import exists, join

import requests
from json_database import JsonStorage
from mycroft_bus_client import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_config_home


class BrightnessControlRPIPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-brightness-control-rpi", config=config)
        self.bus = bus
        self.device_interface = "DSI"
        self.ddcutil_detected_bus = None
        self.ddcutil_brightness_code = None
        self.auto_dim_enabled = False
        self.auto_night_mode_enabled = False
        self.timer_thread = None
        self.nightmode_thread = None
        self.geolocate_api_thread = None
        self.location = None
        self.sunset_time = None

        self.geolocate_api()
        self.start_geolocate_api_timer()
        self.is_auto_dim_enabled()
        self.is_auto_night_mode_enabled()

        LOG.info(f"Location is {self.location}")
        LOG.info(f"Sunset time is {self.sunset_time}")

        self.discover()

        self.bus.on("phal.brightness.control.get",
                    self.query_current_brightness)
        self.bus.on("phal.brightness.control.set",
                    self.set_brightness_from_bus)
        self.bus.on("speaker.extension.display.auto.dim.changed",
                    self.is_auto_dim_enabled)
        self.bus.on("speaker.extension.display.auto.nightmode.changed",
                    self.is_auto_night_mode_enabled)
        self.bus.on("gui.page_interaction",
                    self.undim_display)
        self.bus.on("gui.page_gained_focus",
                    self.undim_display)
        self.bus.on("recognizer_loop:wakeword",
                    self.undim_display)
        self.bus.on("recognizer_loop:record_begin",
                    self.undim_display)

    # Check if the auto dim is enabled
    def is_auto_dim_enabled(self, message=None):
        LOG.info("Checking if auto dim is enabled")
        display_config_path_local = join(xdg_config_home(), "OvosDisplay.conf")
        if exists(display_config_path_local):
            display_configuration = JsonStorage(display_config_path_local)
            self.auto_dim_enabled = display_configuration.get(
                "auto_dim", False)
        else:
            self.auto_dim_enabled = False

        if self.auto_dim_enabled:
            self.start_auto_dim()
        else:
            self.stop_auto_dim()

    # Discover the brightness control device interface (HDMI / DSI) on the Raspberry PI
    def discover(self):
        try:
            LOG.info("Discovering brightness control device interface")
            proc = subprocess.Popen(["/opt/vc/bin/vcgencmd",
                                    "get_config", "display_default_lcd"], stdout=subprocess.PIPE)
            if proc.stdout.read().decode("utf-8").strip() == "1":
                self.device_interface = "DSI"
            else:
                self.device_interface = "HDMI"
            LOG.info("Brightness control device interface is {}".format(
                self.device_interface))

            if self.device_interface == "HDMI":
                proc_detect = subprocess.Popen(
                    ["/usr/bin/ddcutil", "detect"], stdout=subprocess.PIPE)

                ddcutil_detected_output = proc_detect.stdout.read().decode("utf-8")
                if "I2C bus:" in ddcutil_detected_output:
                    bus_code = ddcutil_detected_output.split(
                        "I2C bus: ")[1].strip().split("\n")[0]
                    self.ddcutil_detected_bus = bus_code.split("-")[1].strip()
                else:
                    ddcutil_detected_bus = None
                    LOG.error("Display is not detected by DDCUTIL")

                if self.ddcutil_detected_bus:
                    proc_fetch_vcp = subprocess.Popen(
                        ["/usr/bin/ddcutil", "getvcp", "known", "--bus", self.ddcutil_detected_bus], stdout=subprocess.PIPE)
                    # check the vcp output for the Brightness string and get its VCP code
                    for line in proc_fetch_vcp.stdout:
                        if "Brightness" in line.decode("utf-8"):
                            self.ddcutil_brightness_code = line.decode(
                                "utf-8").split(" ")[2].strip()
        except Exception as e:
            LOG.error(e)
            LOG.info("Falling back to DSI interface")
            self.device_interface = "DSI"

    # Get the current brightness level
    def get_brightness(self):
        LOG.info("Getting current brightness level")
        if self.device_interface == "HDMI":
            proc_fetch_vcp = subprocess.Popen(
                ["/usr/bin/ddcutil", "getvcp", self.ddcutil_brightness_code, "--bus", self.ddcutil_detected_bus], stdout=subprocess.PIPE)
            for line in proc_fetch_vcp.stdout:
                if "current value" in line.decode("utf-8"):
                    brightness_level = line.decode(
                        "utf-8").split("current value = ")[1].split(",")[0].strip()
                    return int(brightness_level)

        if self.device_interface == "DSI":
            proc_fetch_vcp = subprocess.Popen(
                ["cat", "/sys/class/backlight/rpi_backlight/actual_brightness"], stdout=subprocess.PIPE)
            for line in proc_fetch_vcp:
                brightness_level = line.decode("utf-8").strip()
                return int(brightness_level)

    def query_current_brightness(self, message):
        current_brightness = self.get_brightness()
        if self.device_interface == "HDMI":
            self.bus.emit(message.response(
                data={"brightness": current_brightness}))
        elif self.device_interface == "DSI":
            brightness_percentage = int((current_brightness / 255) * 100)
            self.bus.emit(message.response(
                data={"brightness": brightness_percentage}))

    # Set the brightness level
    def set_brightness(self, level):
        LOG.debug("Setting brightness level")
        if self.device_interface == "HDMI":
            subprocess.Popen(["/usr/bin/ddcutil", "setvcp", self.ddcutil_brightness_code,
                             "--bus", self.ddcutil_detected_bus, str(level)])
        elif self.device_interface == "DSI":
            subprocess.call(
                f"echo {level} > /sys/class/backlight/rpi_backlight/brightness", shell=True)

        LOG.info("Brightness level set to {}".format(level))

    def set_brightness_from_bus(self, message):
        LOG.debug("Setting brightness level from bus")
        level = message.data.get("brightness", "")

        if self.device_interface == "HDMI":
            percent_level = 100 * float(level)
            if float(level) < 0:
                apply_level = 0
            elif float(level) > 100:
                apply_level = 100
            else:
                apply_level = round(percent_level / 10) * 10

            self.set_brightness(apply_level)

        if self.device_interface == "DSI":
            percent_level = 255 * float(level)
            if float(level) < 0:
                apply_level = 0
            elif float(level) > 255:
                apply_level = 255
            else:
                apply_level = round(percent_level / 10) * 10

            self.set_brightness(apply_level)

    def start_auto_dim(self):
        LOG.debug("Starting auto dim")
        self.timer_thread = threading.Thread(target=self.auto_dim_timer)
        self.timer_thread.start()

    def auto_dim_timer(self):
        while self.auto_dim_enabled:
            time.sleep(60)
            LOG.debug("Adjusting brightness automatically")
            if self.device_interface == "HDMI":
                current_brightness = 100
            if self.device_interface == "DSI":
                current_brightness = 255

            self.bus.emit(
                Message("phal.brightness.control.auto.dim.update", {"brightness": 20}))
            self.set_brightness(20)

    def stop_auto_dim(self):
        LOG.debug("Stopping Auto Dim")
        self.auto_dim_enabled = False
        if self.timer_thread:
            self.timer_thread.join()

    def restart_auto_dim(self):
        LOG.debug("Restarting Auto Dim")
        self.stop_auto_dim()
        self.auto_dim_enabled = True
        self.start_auto_dim()

    def undim_display(self, message=None):
        if self.auto_dim_enabled:
            LOG.debug("Undimming display on interaction")
            if self.device_interface == "HDMI":
                self.set_brightness(100)
            if self.device_interface == "DSI":
                self.set_brightness(255)
            self.bus.emit(
                Message("phal.brightness.control.auto.dim.update", {"brightness": "100"}))
            self.restart_auto_dim()
        else:
            pass

    ##### AUTO NIGHT MODE HANDLING #####

    def get_time_of_day(self):
        LOG.debug("Getting time of day")
        now = datetime.datetime.now()
        return now.time()

    def check_if_sun_has_set(self):
        LOG.debug("Checking if sun has set")
        # check if the time now is after the sunset time
        current_time = self.get_time_of_day()
        sunset_time = self.sunset_time.time()
        if self.sunset_time:
            if current_time > sunset_time:
                return True
            else:
                return False
        else:
            return False

    def get_sunset_time(self):
        LOG.debug("Getting sunset time")
        if self.location:
            location_lat = self.location["coordinate"]["latitude"]
            location_lon = self.location["coordinate"]["longitude"]
            response = requests.get(
                f"http://api.sunrise-sunset.org/json?lat={location_lat}&lng={location_lon}&formatted=0")
            response_json = response.json()
            sunset_time_str = response_json["results"]["sunset"]
            sunset_time = datetime.datetime.strptime(
                sunset_time_str, "%Y-%m-%dT%H:%M:%S%z")
            self.sunset_time = sunset_time
        else:
            # Set the sunset time to 10:00pm if no location is set
            self.sunset_time = datetime.time(22, 0)

    def start_auto_night_mode(self):
        LOG.debug("Starting auto night mode")
        self.nightmode_thread = threading.Thread(
            target=self.auto_night_mode_timer)
        self.nightmode_thread.start()

    def auto_night_mode_timer(self):
        while self.auto_night_mode_enabled:
            time.sleep(60)
            LOG.debug("Checking if it is night time")
            if self.check_if_sun_has_set():
                LOG.debug("It is night time")
                self.bus.emit(
                    Message("phal.brightness.control.auto.night.mode.enabled"))

    def stop_auto_night_mode(self):
        LOG.debug("Stopping auto night mode")
        self.auto_night_mode_enabled = False
        if self.nightmode_thread:
            self.nightmode_thread.join()

    def is_auto_night_mode_enabled(self):
        display_config_path_local = join(xdg_config_home(), "OvosDisplay.conf")
        if exists(display_config_path_local):
            display_configuration = JsonStorage(display_config_path_local)
            self.auto_night_mode_enabled = display_configuration.get(
                "auto_nightmode", False)
        else:
            self.auto_night_mode_enabled = False

        if self.auto_night_mode_enabled:
            self.start_auto_night_mode()
        else:
            self.stop_auto_night_mode()

    def geolocate_api(self):
        LOG.debug("Getting Geolocation")
        try:
            response = requests.get("http://ip-api.com/json")
            response_json = response.json()
            self.location = {
                "name": response_json["city"],
                "coordinate": {
                    "latitude": response_json["lat"],
                    "longitude": response_json["lon"]
                },
                "timezone": response_json["timezone"],
                "country": response_json["country"]
            }
        except Exception as e:
            LOG.error("Error getting Geolocation")
            LOG.error(e)
            self.location = None

        self.get_sunset_time()

    def geolocate_api_timer(self):
        while True:
            time.sleep(14400)
            self.geolocate_api()

    def start_geolocate_api_timer(self):
        self.geolocate_api_thread = threading.Thread(
            target=self.geolocate_api_timer)
        self.geolocate_api_thread.start()

    def stop_geolocate_api_timer(self):
        if self.geolocate_api_thread:
            self.geolocate_api_thread.join()
