import random
from os.path import dirname, join
from time import sleep

import pexpect
from mycroft_bus_client.message import Message, dig_for_message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.gui import GUIInterface
from ovos_utils.log import LOG


class BalenaWifiSetupPlugin(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-balena-wifi", config=config)
        LOG.info(f"self.config={self.config}")

        self._max_errors = 5
        self.gui = GUIInterface(bus=self.bus, skill_id=self.name)
        self.client_active = False
        self.client_id = None
        self.registered = False
        
        self.wifi_process = None
        self.debug = self.config.get("debug")  # dev setting, VERY VERBOSE DIALOGS
        self.ssid = self.config.get("ssid") or "OVOS"
        self.pswd = self.config.get("psk") or None
        self.portal = self.config.get("portal") or "start dot openvoiceos dot com"
        self.device_name = self.config.get("device") or "OVOS Device"
        self.image_connect_to_ap = self.config.get("image_connect_ap") or \
            "1_phone_connect-to-ap.png"
        self.image_choose_wifi = self.config.get("image_choose_wifi") or \
            "3_phone_choose-wifi.png"
        self.wifi_command = "sudo /usr/local/sbin/wifi-connect --portal-ssid {ssid}"
        if self.pswd:
            self.wifi_command += " --portal-passphrase {pswd}"
        self.color = self.config.get("color") or "#FF0000"
        
        # WIFI Plugin Registeration and Activation Specific Events        
        self.bus.on("ovos.phal.wifi.plugin.stop.setup.event", self.handle_stop_setup)
        self.bus.on("ovos.phal.wifi.plugin.client.registered", self.handle_registered)
        self.bus.on("ovos.phal.wifi.plugin.client.deregistered", self.handle_deregistered)
        self.bus.on("ovos.phal.wifi.plugin.client.registration.failure", self.handle_registration_failure)
        self.bus.on("ovos.phal.wifi.plugin.alive", self.register_client)
        
        # Try Register the Client with WIFI Plugin on Startup
        self.register_client()
        
    # Wifi Plugin Registeration Handling
    def register_client(self, message=None):
        self.bus.emit(Message("ovos.phal.wifi.plugin.register.client", {
            "client": self.name,
            "type": "Remote",
            "display_text": "On Mobile Setup",
            "has_gui": True,
            "requires_input": False
        }))
        
    def handle_registered(self, message=None):
        get_client = message.data.get("client", "")
        if get_client == self.name:
            get_id = message.data.get("id", "")
            self.client_id = get_id
            self.registered = True        
            self.bus.on(f"ovos.phal.wifi.plugin.activate.{self.client_id}", self.handle_activate_client_request)
            self.bus.on(f"ovos.phal.wifi.plugin.deactivate.{self.client_id}", self.handle_deactivate_client_request)
            LOG.info(f"Client Registered with WIFI Plugin: {self.client_id}")
    
    def handle_deregistered(self, message=None):
        self.registered = False
        self.bus.remove(f"ovos.phal.wifi.plugin.activate.{self.client_id}", self.handle_active_client_request)
        self.bus.remove(f"ovos.phal.wifi.plugin.deactivate.{self.client_id}", self.handle_deactivate_client_request)
        self.client_id = None
        
    def handle_registration_failure(self, message=None):
        if not self.registered:
            error = message.data.get("error", "")
            LOG.info(f"Registration Failure: {error}")
            # Try to Register the Client with WIFI Plugin Again
            self.register_client()
            
    def handle_activate_client_request(self, message=None):
        """
        Handles an ovos.phal.wifi.plugin.activate.{self.client_id} request.
        This sets the internal `client_active` flag to True and
        calls `display_network_setup`.
        """
        LOG.info("Balena Wifi Plugin Activated")
        error_count = 0
        self.client_active = True
        while error_count < self._max_errors and \
                not self.display_network_setup():
            LOG.info("Setup failed, retrying")
            error_count += 1
        if error_count >= self._max_errors:
            self.handle_stop_setup()
        if self.debug:
            self.speak_dialog("debug_end_setup")
        self.handle_stop_setup()
        
    def handle_deactivate_client_request(self, message=None):
        """
        Handles an ovos.phal.wifi.plugin.activate.{self.client_id} request.
        This sets the internal `client_active` flag to False and
        calls `cleanup_wifi_process`.
        """
        LOG.info("Balena Wifi Plugin Deactivated")
        self.cleanup_wifi_process()
        self.client_active = False
        self.gui.release()
        
    def request_deactivate(self, message=None):
        self.bus.emit(Message("ovos.phal.wifi.plugin.remove.active.client", {
                      "client": "ovos-PHAL-plugin-balena-wifi"}))
        LOG.info("Balena Wifi Plugin Deactivation Requested")
        
    def display_network_setup(self):
        """
        Start a Balena Wifi process and monitor the output.
        If an error occurs, this method is called recursively to clean up the
        failed instance and start a new one.
        """
        LOG.info("Balena Wifi In Network Setup")
        # Always start with a clean slate
        self.cleanup_wifi_process()
        LOG.info(f"Spawning new wifi_process")
        self.wifi_process = pexpect.spawn(
            self.wifi_command.format(ssid=self.ssid)
        )
        # https://github.com/pexpect/pexpect/issues/462
        self.wifi_process.delayafterclose = 1
        self.wifi_process.delayafterterminate = 1
        prev = ""
        restart = False
        if self.debug:
            self.speak_dialog("debug_start_setup")
        in_setup = True

        while in_setup and self.client_active:
            restart = False
            try:
                out = self.wifi_process.readline().decode("utf-8").strip()
                if out == prev:
                    continue
                prev = out
                if out.startswith("Access points: "):
                    aps = list(out.split("Access points: ")[-1])
                    LOG.info(out)
                    if self.debug:
                        self.speak_dialog("debug_wifi_scanned")
                elif out.startswith("Starting access point..."):
                    if self.debug:
                        self.speak_dialog("debug_ap_start")
                elif out.startswith("Access point ") and \
                        out.endswith("created"):
                    self.prompt_to_join_ap()
                    if self.debug:
                        self.speak_dialog("debug_ap_created")
                elif out.startswith("Starting HTTP server on"):
                    LOG.debug(out)
                    if self.debug:
                        self.speak_dialog("debug_http_started")
                elif out.startswith("Stopping access point"):
                    if self.debug:
                        self.speak_dialog("debug_ap_stop")
                elif out.startswith("Access point ") and \
                        out.endswith("stopped"):
                    if self.debug:
                        self.speak_dialog("debug_ap_stopped")
                elif out == "User connected to the captive portal":
                    LOG.info(out)
                    self.prompt_to_select_network()
                    if self.debug:
                        self.speak_dialog("debug_user_connected")
                elif out.startswith("Connecting to access point"):
                    if self.debug:
                        self.speak_dialog("debug_connecting")
                elif out.startswith("Internet connectivity established"):
                    LOG.info(out)
                    in_setup = False
                    self.report_setup_complete()
                    if self.debug:
                        self.speak_dialog("debug_wifi_connected")
                elif any((x in out for x in
                          ("Error", "[Errno",
                           "Connection to access point not activated"))):
                    LOG.error(out)
                    # TODO figure out at least the errors handled gracefully
                    accepted_errors = [
                        "Password length should be at least 8 characters",
                        "Get org.freedesktop.NetworkManager.AccessPoint::RsnFlags property failed"
                    ]
                    for e in accepted_errors:
                        if e in out:
                            continue
                    else:
                        self.report_setup_failed()
                        restart = True
                        break

                if self.debug:
                    LOG.info(out)
            except pexpect.exceptions.EOF:
                # exited
                LOG.info("Exited wifi setup process")
                break
            except pexpect.exceptions.TIMEOUT:
                # nothing happened for a while
                pass
            except KeyboardInterrupt:
                break
            except Exception as e:
                LOG.exception(e)
                break

        return not restart  # Return True on success

    # GUI events
    def prompt_to_join_ap(self, message=None):
        """Provide instructions for setting up wifi."""
        self.manage_setup_display("join-ap", "prompt")
        self.speak_dialog("wifi_intro_2", {"ssid": self.ssid,
                                           "portal": self.portal})
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(2)

    def prompt_to_select_network(self, message=None):
        """Prompt user to select network and login."""
        self.manage_setup_display("select-network", "prompt")
        self.speak_dialog("wifi_intro_3", {"portal": self.portal,
                                           "device": self.device_name})
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(2)

    def report_setup_complete(self, message=None):
        """Wifi setup complete, network is connected."""
        self.manage_setup_display("setup-completed", "status")
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(5)
        self.bus.emit(Message("ovos.wifi.setup.completed"))
        self.client_active = False
        self.request_deactivate()

    def report_setup_failed(self, message=None):
        """Wifi setup failed"""
        # self.in_setup = False
        self.manage_setup_display("setup-failed", "status")
        self.speak_dialog("debug_wifi_error")
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(5)
        # self.display_network_setup()  The setup loop will do this

    def manage_setup_display(self, state, page_type):
        self.gui.clear()
        page = join(dirname(__file__), "ui", "NetworkLoader.qml")
        if state == "join-ap" and page_type == "prompt":
            self.gui["image"] = self.image_connect_to_ap
            self.gui["label"] = "Connect to the Wi-Fi network"
            self.gui["highlight"] = self.ssid
            self.gui["color"] = self.color
            self.gui["page_type"] = "Prompt"
            self.gui.show_page(page, override_animations=True, override_idle=True)
        elif state == "select-network" and page_type == "prompt":
            self.gui["image"] = self.image_choose_wifi
            self.gui["label"] = "Select local Wi-Fi network to connect"
            self.gui["highlight"] = self.device_name
            self.gui["color"] = self.color
            self.gui["page_type"] = "Prompt"
            self.gui.show_page(page, override_animations=True, override_idle=True)
        elif state == "setup-completed" and page_type == "status":
            self.gui["image"] = "icons/check-circle.svg"
            self.gui["label"] = "Connected"
            self.gui["highlight"] = ""
            self.gui["color"] = "#40DBB0"
            self.gui["page_type"] = "Status"
            self.gui.show_page(page, override_animations=True)
        elif state == "setup-failed" and page_type == "status":
            self.gui["image"] = "icons/times-circle.svg"
            self.gui["label"] = "Connection Failed"
            self.gui["highlight"] = ""
            self.gui["color"] = "#FF0000"
            self.gui["page_type"] = "Status"
            self.gui.show_page(page, override_animations=True)

    # cleanup
    def cleanup_wifi_process(self):
        if self.wifi_process is not None:
            try:
                if self.wifi_process.isalive():
                    LOG.debug("terminating wifi setup process")
                    self.wifi_process.sendcontrol('c')
                    sleep(1)
                    self.wifi_process.close()
                    sleep(1)
                if self.wifi_process.isalive():
                    LOG.warning('wifi setup did not exit gracefully.')
                    self.wifi_process.close(force=True)
                    sleep(1)
                    if self.wifi_process.isalive():
                        LOG.warning('trying to terminate wifi setup process')
                        self.wifi_process.terminate()
                        sleep(1)
                        if self.wifi_process and self.wifi_process.isalive():
                            raise Exception("self.wifi_process not terminated!")
                    self.wifi_process = None
                else:
                    LOG.debug('wifi setup exited gracefully.')
                    self.wifi_process = None
            except Exception as e:
                LOG.exception(e)
        else:
            return
    
    def handle_stop_setup(self, message=None):
        self.request_deactivate()
    
    def shutdown(self):
        self.handle_stop_setup()
        super().shutdown()

    # speech
    @property
    def lang(self):
        return self.config.get("lang") or \
               self.config_core.get("lang") or \
               "en-us"

    def speak_dialog(self, key, data: dict = None):
        """ Speak a random sentence from a dialog file.
        Args:
            key (str): dialog file key (e.g. "hello" to speak from the file
                                        "locale/en-us/hello.dialog")
            data (dict): dict of dialog entity substitutions
        """
        dialog_file = join(dirname(__file__), "locale", self.lang, key + ".dialog")
        with open(dialog_file) as f:
            utterances = [u for u in f.read().split("\n")
                          if u.strip() and not u.startswith("#")]
        utterance = random.choice(utterances)
        if data:
            for d in data:
                utterance = utterance.replace('{{' + d + '}}', data[d])
        meta = {'dialog': key,
                'skill': self.name}
        data = {'utterance': utterance,
                'expect_response': False,
                'meta': meta,
                'lang': self.lang}
        message = dig_for_message()
        m = message.forward("speak", data) if message else Message("speak", data)
        m.context["skill_id"] = self.name
        self.bus.emit(m)
