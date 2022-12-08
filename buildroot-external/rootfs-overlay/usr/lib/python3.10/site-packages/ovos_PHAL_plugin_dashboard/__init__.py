import os
import time
import secrets
import string
import subprocess
from ovos_utils.log import LOG
from ovos_utils.network_utils import get_ip
from mycroft_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin


class OVOSDashboardPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-dashboard", config=config)
        self.bus = bus
        self.bus.on("ovos.PHAL.dashboard.enable",
                    self.handle_device_developer_enable_dash)
        self.bus.on("ovos.PHAL.dashboard.disable",
                    self.handle_device_developer_disable_dash)
        self.bus.on("ovos.PHAL.dashboard.get.status",
                    self.handle_device_dashboard_status_check)

        # Dashboard Specific
        self.dash_running = None
        alphabet = string.ascii_letters + string.digits
        self.dash_secret = ''.join(secrets.choice(alphabet) for i in range(5))

        LOG.info("Dashboard Plugin Initalized")

    def handle_device_dashboard_status_check(self, _):
        build_status_check_call = "systemctl --user is-active --quiet ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        status = os.system(build_status_check_call)

        if status == 0:
            self.dash_running = True
        else:
            self.dash_running = False

        if self.dash_running:
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response", {
                          "status": True, "url": "https://{0}:5000".format(get_ip()), "user": "OVOS", "password": self.dash_secret}))
        else:
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response", {
                          "status": False, "url": None, "user": None, "password": None}))

    def handle_device_developer_enable_dash(self, message):
        os.environ["SIMPLELOGIN_USERNAME"] = "OVOS"
        os.environ["SIMPLELOGIN_PASSWORD"] = self.dash_secret
        build_call = "systemctl --user start ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        call_dash = subprocess.Popen([build_call], shell=True)
        time.sleep(3)
        build_status_check_call = "systemctl --user is-active --quiet ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        status = os.system(build_status_check_call)

        if status == 0:
            self.dash_running = True
        else:
            self.dash_running = False

        if self.dash_running:
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response", {
                          "status": True, "url": "https://{0}:5000".format(get_ip()), "user": "OVOS", "password": self.dash_secret}))

    def handle_device_developer_disable_dash(self, message):
        build_call = "systemctl --user stop ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        subprocess.Popen([build_call], shell=True)
        time.sleep(3)
        build_status_check_call = "systemctl --user is-active --quiet ovos-dashboard@'{0}'.service".format(
            self.dash_secret)
        status = os.system(build_status_check_call)

        if status == 0:
            self.dash_running = True
        else:
            self.dash_running = False

        if not self.dash_running:
            self.bus.emit(Message("ovos.PHAL.dashboard.status.response", {
                          "status": False, "url": None, "user": None, "password": None}))
