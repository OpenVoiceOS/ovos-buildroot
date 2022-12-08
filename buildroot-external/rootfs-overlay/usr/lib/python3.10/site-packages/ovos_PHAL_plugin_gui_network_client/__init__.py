import random
from os.path import dirname, join
from time import sleep

from mycroft_bus_client.message import Message, dig_for_message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.gui import GUIInterface
from ovos_utils.log import LOG
from ovos_utils.network_utils import is_connected, get_ip


class GuiNetworkClientPlugin(PHALPlugin):

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-gui-network-client", config=config)
        self.gui = GUIInterface(bus=self.bus, skill_id=self.name)
        self.connected_network = None
        self.client_active = False
        self.client_id = None
        self.registered = False
        
        # WIFI Plugin Registeration and Activation Specific Events        
        self.bus.on("ovos.phal.wifi.plugin.stop.setup.event", self.handle_stop_setup)
        self.bus.on("ovos.phal.wifi.plugin.client.registered", self.handle_registered)
        self.bus.on("ovos.phal.wifi.plugin.client.deregistered", self.handle_deregistered)
        self.bus.on("ovos.phal.wifi.plugin.client.registration.failure", self.handle_registration_failure)
        self.bus.on("ovos.phal.wifi.plugin.alive", self.register_client)
        
        # OVOS PHAL NM EVENTS
        self.bus.on("ovos.phal.nm.connection.successful", self.display_success)
        self.bus.on("ovos.phal.nm.connection.failure", self.display_failure)

        # INTERNAL GUI EVENTS
        self.bus.on("ovos.phal.gui.network.client.back",
                    self.display_path_exit)
        self.bus.on("ovos.phal.gui.display.connected.network.settings",
                    self.display_connected_network_settings)
        self.bus.on("ovos.phal.gui.display.disconnected.network.settings",
                    self.display_disconnected_network_settings)
        self.bus.on("ovos.phal.gui.network.client.internal.back",
                    self.display_internal_back)
        
        # Also listen for certain events that can forcefully deactivate the client
        self.bus.on("system.display.homescreen", self.clean_shutdown)
        self.bus.on("mycroft.device.settings", self.clean_shutdown)
        
        # Try Register the Client with WIFI Plugin on Startup
        self.register_client()
        
    # Wifi Plugin Registeration Handling
    def register_client(self, message=None):
        self.bus.emit(Message("ovos.phal.wifi.plugin.register.client", {
            "client": self.name,
            "type": "onDevice",
            "display_text": "On Device Setup",
            "has_gui": True,
            "requires_input": True
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
        LOG.info("Gui Network Client Plugin Activated")
        if self.client_active:
            self.request_deactivate()

        self.client_active = True
        self.display_network_setup()

    def handle_deactivate_client_request(self, message=None):
        LOG.info("Gui Network Client Plugin Deactivated")
        self.client_active = False
        self.gui.release()

    def request_deactivate(self, message=None):
        self.bus.emit(Message("ovos.phal.wifi.plugin.remove.active.client", {
                      "client": "ovos-PHAL-plugin-gui-network-client"}))
        LOG.info("Gui Network Client Plugin Deactivation Requested")

    # Actual GUI Networking Operations
    def display_network_setup(self, message=None):
        LOG.info("In Display Network Setup")     
        self.manage_setup_display("select-network", "network")

    def display_path_exit(self, message=None):
        self.client_active = False
        self.request_deactivate()

        if not is_connected():
            self.bus.emit(Message("ovos.phal.wifi.plugin.user.activated"))
        else:
            self.gui.release()

    def clean_shutdown(self, message=None):
        if self.client_active:
            self.request_deactivate()
            self.gui.release()

    def display_connected_network_settings(self, message=None):
        self.connected_network_details = message.data.get("connection_details", {})
        self.gui["connectionDetails"] = self.connected_network_details
        self.gui["ipAddress"] = get_ip()
        self.manage_setup_display("connected-network-settings", "network")

    def display_disconnected_network_settings(self, message=None):
        self.disconnected_network_details = message.data.get("connection_details", {})
        self.gui["connectionDetails"] = self.disconnected_network_details
        self.manage_setup_display("disconnected-network-settings", "network")

    def display_internal_back(self, message=None):
        self.manage_setup_display("select-network", "network")

    def display_success(self, message=None):
        self.manage_setup_display("setup-completed", "status")
        sleep(5)
        self.bus.emit(Message("ovos.wifi.setup.completed"))
        self.client_active = False
        self.request_deactivate()

    def display_failure(self, message=None):
        """Wifi setup failed"""       
        errorCode = message.data.get("errorCode", "")
        if errorCode == "0":
            self.display_failed_password()
        else:
            self.manage_setup_display("setup-failed", "status")
            self.speak_dialog("debug_wifi_error")
            sleep(5)
            self.display_network_setup()   

    def display_failed_password(self):
        self.manage_setup_display("incorrect-password", "status")
        self.speak_dialog("debug_wifi_error")
        sleep(5)
        self.display_network_setup()

    def manage_setup_display(self, state, page_type):
        self.log.info("In Displaying Page Function")
        page = join(dirname(__file__), "ui", "GuiClientLoader.qml")
        if state == "select-network" and page_type == "network":
            self.gui["page_type"] = "NetworkingLoader"
            self.gui["image"] = ""
            self.gui["label"] = ""
            self.gui["color"] = ""
            self.gui.show_page(page, override_idle=True,
                               override_animations=True)
        elif state == "connected-network-settings" and page_type == "network":
            self.gui["page_type"] = "ManageConnectedNetwork"
            self.gui.show_page(page, override_idle=True,
                               override_animations=True)
        elif state == "disconnected-network-settings" and page_type == "network":
            self.gui["page_type"] = "ManageUnconnectedNetwork"
            self.gui.show_page(page, override_idle=True,
                               override_animations=True)
        elif state == "setup-completed" and page_type == "status":
            self.gui["page_type"] = "Status"
            self.gui["image"] = "icons/check-circle.svg"
            self.gui["label"] = "Connected"
            self.gui["color"] = "#40DBB0"
            self.gui.show_page(page, override_animations=True)
        elif state == "setup-failed" and page_type == "status":
            self.gui["page_type"] = "Status"
            self.gui["image"] = "icons/times-circle.svg"
            self.gui["label"] = "Connection Failed"
            self.gui["color"] = "#FF0000"
            self.gui.show_page(page, override_animations=True)
        elif state == "incorrect-password" and page_type == "status":
            self.gui["page_type"] = "Status"
            self.gui["image"] = "icons/times-circle.svg"
            self.gui["label"] = "Incorrect Password"
            self.gui["color"] = "#FF0000"
            self.gui.show_page(page, override_animations=True)
            
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

    def speak_dialog(self, key):
        """ Speak a random sentence from a dialog file.
        Args:
            key (str): dialog file key (e.g. "hello" to speak from the file
                                        "locale/en-us/hello.dialog")
        """
        dialog_file = join(dirname(__file__), "locale",
                           self.lang, key + ".dialog")
        with open(dialog_file) as f:
            utterances = [u for u in f.read().split("\n")
                          if u.strip() and not u.startswith("#")]
        utterance = random.choice(utterances)
        meta = {'dialog': key,
                'skill': self.name}
        data = {'utterance': utterance,
                'expect_response': False,
                'meta': meta,
                'lang': self.lang}
        message = dig_for_message()
        m = message.forward(
            "speak", data) if message else Message("speak", data)
        m.context["skill_id"] = self.name
        self.bus.emit(m)
