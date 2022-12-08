import os
import shutil
import subprocess
from os.path import dirname, join
from threading import Event

from json_database import JsonStorageXDG, JsonDatabaseXDG
from mycroft_bus_client import Message
from ovos_backend_client.identity import IdentityManager
from ovos_config.config import update_mycroft_config
from ovos_config.locale import set_default_lang
from ovos_config.locations import OLD_USER_CONFIG, USER_CONFIG, WEB_CONFIG_CACHE
from ovos_config.meta import get_xdg_base
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.gui import GUIInterface
from ovos_utils.system import system_shutdown, system_reboot, ssh_enable, ssh_disable, ntp_sync, restart_service, \
    is_process_running
from ovos_utils.xdg_utils import xdg_state_home, xdg_cache_home, xdg_data_home


class SystemEventsValidator:
    @staticmethod
    def validate(config=None):
        """ this method is called before loading the plugin.
        If it returns False the plugin is not loaded.
        This allows a plugin to run platform checks"""
        return True


class SystemEvents(PHALPlugin):
    validator = SystemEventsValidator

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-system", config=config)
        self.gui = GUIInterface(bus=self.bus, skill_id=self.name)

        self.bus.on("system.ntp.sync", self.handle_ntp_sync_request)
        self.bus.on("system.ssh.enable", self.handle_ssh_enable_request)
        self.bus.on("system.ssh.disable", self.handle_ssh_disable_request)
        self.bus.on("system.reboot", self.handle_reboot_request)
        self.bus.on("system.shutdown", self.handle_shutdown_request)
        self.bus.on("system.factory.reset", self.handle_reset_register)
        self.bus.on("system.factory.reset.register", self.handle_factory_reset_request)
        self.bus.on("system.configure.language", self.handle_configure_language_request)
        self.bus.on("system.mycroft.service.restart",
                    self.handle_mycroft_restart_request)
        self.service_name = config.get("core_service") or "mycroft.service"
        self.use_root = config.get("sudo", True)

        self.factory_reset_plugs = []

        # trigger register events from phal plugins
        self.bus.emit(Message("system.factory.reset.ping"))

    @property
    def use_external_factory_reset(self):
        # see if PHAL service / mycroft.conf requested external handling
        external_requested = self.config.get("use_external_factory_reset")
        # auto detect ovos-shell if no explicit preference
        if external_requested is None and is_process_running("ovos-shell"):
            return True
        return external_requested or False

    def handle_reset_register(self, message):
        sid = message.data["skill_id"]
        if sid not in self.factory_reset_plugs:
            self.factory_reset_plugs.append(sid)

    def handle_factory_reset_request(self, message):
        self.bus.emit(message.forward("system.factory.reset.start"))
        self.bus.emit(message.forward("system.factory.reset.ping"))

        if os.path.isfile(IdentityManager.OLD_IDENTITY_FILE):
            os.remove(IdentityManager.OLD_IDENTITY_FILE)
        if os.path.isfile(IdentityManager.IDENTITY_FILE):
            os.remove(IdentityManager.IDENTITY_FILE)

        wipe_cache = message.data.get("wipe_cache", True)
        if wipe_cache:
            p = f"{xdg_cache_home()}/{get_xdg_base()}"
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)

        wipe_data = message.data.get("wipe_data", True)
        if wipe_data:
            p = f"{xdg_data_home()}/{get_xdg_base()}"
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)

            # misc json databases from offline/personal backend
            for j in ["ovos_device_info",
                      "ovos_oauth",
                      "ovos_oauth_apps",
                      "ovos_devices",
                      "ovos_metrics",
                      "ovos_preferences",
                      "ovos_skills_meta"]:
                p = JsonStorageXDG(j).path
                if os.path.isfile(p):
                    os.remove(p)
            for j in ["ovos_metrics",
                      "ovos_utterances",
                      "ovos_wakewords"]:
                p = JsonDatabaseXDG(j).db.path
                if os.path.isfile(p):
                    os.remove(p)

        wipe_logs = message.data.get("wipe_logs", True)
        if wipe_logs:
            p = f"{xdg_state_home()}/{get_xdg_base()}"
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)

        wipe_cfg = message.data.get("wipe_configs", True)
        if wipe_cfg:
            if os.path.isfile(OLD_USER_CONFIG):
                os.remove(OLD_USER_CONFIG)
            if os.path.isfile(USER_CONFIG):
                os.remove(USER_CONFIG)
            if os.path.isfile(WEB_CONFIG_CACHE):
                os.remove(WEB_CONFIG_CACHE)

        reset_phal = message.data.get("reset_hardware", True)
        if reset_phal and len(self.factory_reset_plugs):
            reset_plugs = []
            event = Event()

            def on_done(message):
                nonlocal reset_plugs, event
                sid = message.data["skill_id"]
                if sid not in reset_plugs:
                    reset_plugs.append(sid)
                if all([s in reset_plugs for s in self.factory_reset_plugs]):
                    event.set()

            self.bus.on("system.factory.reset.phal.complete", on_done)
            self.bus.emit(message.forward("system.factory.reset.phal"))
            event.wait(timeout=60)
            self.bus.remove("system.factory.reset.phal.complete", on_done)

        script = message.data.get("script", True)
        if script:
            script = os.path.expanduser(self.config.get("reset_script", ""))
            if os.path.isfile(script):
                if self.use_external_factory_reset:
                    self.bus.emit(Message("ovos.shell.exec.factory.reset", {"script": script}))
                    # OVOS shell will handle all external operations here to exec script
                    # including sending complete event to whoever is listening
                else:
                    subprocess.call(script, shell=True)
                    self.bus.emit(message.forward("system.factory.reset.complete"))
                    reboot = message.data.get("reboot", True)
                    if reboot:
                        self.bus.emit(message.forward("system.reboot"))

    def handle_ssh_enable_request(self, message):
        ssh_enable()
        # ovos-shell does not want to display
        if message.data.get("display", True):
            page = join(dirname(__file__), "ui", "Status.qml")
            self.gui["status"] = "Enabled"
            self.gui["label"] = "SSH Enabled"
            self.gui.show_page(page)

    def handle_ssh_disable_request(self, message):
        ssh_disable()
        # ovos-shell does not want to display
        if message.data.get("display", True):
            page = join(dirname(__file__), "ui", "Status.qml")
            self.gui["status"] = "Disabled"
            self.gui["label"] = "SSH Disabled"
            self.gui.show_page(page)

    def handle_ntp_sync_request(self, message):
        ntp_sync()
        # NOTE: this one defaults to False
        # it is usually part of other groups of actions that may provide their own UI
        if message.data.get("display", False):
            page = join(dirname(__file__), "ui", "Status.qml")
            self.gui["status"] = "Enabled"
            self.gui["label"] = "Clock updated"
            self.gui.show_page(page)
        self.bus.emit(message.reply('system.ntp.sync.complete'))

    def handle_reboot_request(self, message):
        if message.data.get("display", True):
            page = join(dirname(__file__), "ui", "Reboot.qml")
            self.gui.show_page(page, override_animations=True, override_idle=True)
        system_reboot()

    def handle_shutdown_request(self, message):
        if message.data.get("display", True):
            page = join(dirname(__file__), "ui", "Shutdown.qml")
            self.gui.show_page(page, override_animations=True, override_idle=True)
        system_shutdown()

    def handle_configure_language_request(self, message):
        language_code = message.data.get('language_code', "en_US")
        with open(f"{os.environ['HOME']}/.bash_profile", "w") as bash_profile_file:
            bash_profile_file.write(f"export LANG={language_code}\n")

        language_code = language_code.lower().replace("_", "-")
        set_default_lang(language_code)
        update_mycroft_config({"lang": language_code}, bus=self.bus)

        # NOTE: this one defaults to False
        # it is usually part of other groups of actions that may provide their own UI
        if message.data.get("display", False):
            page = join(dirname(__file__), "ui", "Status.qml")
            self.gui["status"] = "Enabled"
            self.gui["label"] = f"Language changed to {language_code}"
            self.gui.show_page(page)

        self.bus.emit(Message('system.configure.language.complete',
                              {"lang": language_code}))

    def handle_mycroft_restart_request(self, message):
        if message.data.get("display", True):
            page = join(dirname(__file__), "ui", "Restart.qml")
            self.gui.show_page(page, override_animations=True, override_idle=True)
        restart_service(self.service_name, sudo=self.use_root)

    def shutdown(self):
        self.bus.remove("system.ntp.sync", self.handle_ntp_sync_request)
        self.bus.remove("system.ssh.enable", self.handle_ssh_enable_request)
        self.bus.remove("system.ssh.disable", self.handle_ssh_disable_request)
        self.bus.remove("system.reboot", self.handle_reboot_request)
        self.bus.remove("system.shutdown", self.handle_shutdown_request)
        self.bus.remove("system.factory.reset", self.handle_factory_reset_request)
        self.bus.remove("system.factory.reset.register", self.handle_reset_register)
        self.bus.remove("system.configure.language", self.handle_configure_language_request)
        self.bus.remove("system.mycroft.service.restart", self.handle_mycroft_restart_request)
        super().shutdown()
