import asyncio
import subprocess
import threading

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from mycroft_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG


# Event Documentation
# ===================
# Backend:
# ovos.phal.nm.set.backend
# - type: Request
# - description: Allows client to use a specific backend
#
# ovos.phal.nm.backend.not.supported
# - type: Response
# - description: Emitted when plugin does not support the
# specific backend
#
# Scanning: 
# ovos.phal.nm.scan
# - type: Request
# - description: Allows client to request for a network scan
#
# ovos.phal.nm.scan.complete
# - type: Response
# - description: Emited when the requested scan is completed
# with a network list
#
# Connecting:
# ovos.phal.nm.connect
# - type: Request
# - description: Allows clients to connect to a given network
#
# ovos.phal.nm.connection.successful
# - type: Response
# - description: Emitted when a connection is successfully established
#
# ovos.phal.nm.connection.failure
# - type: Response
# - description: Emitted when a connection fails to establish
#
# Disconnecting:
# ovos.phal.nm.disconnect
# - type: Request
# - description: Allows clients to disconnect from a network
#
# ovos.phal.nm.disconnection.successful
# - type: Response
# - description: Emitted when a connection successfully disconnects
#
# ovos.phal.nm.disconnection.failure
# - type: Response
# - description: Emitted when a connection fails to disconnect
#
# Forgetting:
# ovos.phal.nm.forget
# - type: Request
# - description: Allows a client to forget a network
#
# ovos.phal.nm.forget.successful
# - type: Response
# - description: Emitted when a connection successfully is forgetten
#
# ovos.phal.nm.forget.failure
# - type: Response
# - description: Emitted when a connection fails to forget

class NetworkManagerPlugin(PHALPlugin):

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-network-manager", config=config)
        self.backend = "nmcli"
        self.thread = None
        self.dbus_manager = DbusNetworkManager()
        # Register Network Manager Events
        # The gui client relies on this to connect
        self.bus.on("ovos.phal.nm.set.backend",
                    self.handle_network_backend_set)
        self.bus.on("ovos.phal.nm.scan", self.handle_network_scan_request)
        self.bus.on("ovos.phal.nm.connect",
                    self.handle_network_connect_request)
        self.bus.on("ovos.phal.nm.connect.open.network",
                    self.handle_open_network_connect_request)
        self.bus.on("ovos.phal.nm.reconnect", 
                    self.handle_network_reconnect_request)
        self.bus.on("ovos.phal.nm.disconnect",
                    self.handle_network_disconnect_request)
        self.bus.on("ovos.phal.nm.forget", self.handle_network_forget_request)
        self.bus.on("ovos.phal.nm.get.connected",
                    self.handle_network_connected_query)

    # Network Manager Events

    def handle_network_backend_set(self, message):
        selected_backend = message.data.get("backend", "")
        # We support currently two backends: dbus and nmcli
        # if the selected backend is not supported we will default to nmcli
        if selected_backend == "dbus":
            self.backend = "dbus"
            LOG.info("Network Manager backend set to dbus")
        elif selected_backend == "nmcli":
            self.backend = "nmcli"
            LOG.info("Network Manager backend set to nmcli")
        else:
            self.bus.emit(Message("ovos.phal.nm.backend.not.supported", {
                          "error": "Backend not supported, defaulting to nmcli"}))
            self.backend = "nmcli"
            LOG.warning("Network Manager backend set to nmcli")

    def handle_network_scan_request(self, message):
        LOG.info("Scanning for networks")
        # Scan for networks using Network Manager and build a list of networks found and their security types
        # This is a blocking call so we should run it in a separate thread
        self.thread = threading.Thread(target=self.scan_for_networks)
        self.thread.start()

    def scan_for_networks(self):
        # Scan for networks using Network Manager and build a list of networks found and their security types
        # Target both nmcli and dbus backends
        if self.backend == "dbus":
            LOG.info("Scanning for networks using dbus backend")
            dbus_networks_list = asyncio.run(
                self.dbus_manager.scan_for_networks())
            self.bus.emit(Message("ovos.phal.nm.scan.complete", {
                          "networks": dbus_networks_list}))
        if self.backend == "nmcli":
            LOG.info("Scanning for networks using nmcli backend")
            subprocess.Popen(
                ['nmcli', 'dev', 'wifi', 'rescan']
            )
            scan_process = subprocess.Popen(
                ["nmcli", "--terse", "--fields", "SSID,SECURITY", "device", "wifi", "list"], stdout=subprocess.PIPE)
            scan_output = scan_process.communicate(
            )[0].decode("utf-8").split("\n")
            
            # We will use the output to build a list of networks and their security types
            networks_list = []
            for line in scan_output:
                if line != "":
                    line_split = line.split(":")
                    networks_list.append(
                        {"ssid": line_split[0], "security": line_split[1]})
            # Emit the list of networks and their security types
            self.bus.emit(Message("ovos.phal.nm.scan.complete",
                          {"networks": networks_list}))

        self.thread.join()
        self.thread = None

    def handle_network_connect_request(self, message):
        network_name = message.data.get("connection_name", "")
        secret_phrase = message.data.get("password", "")
        security_type = message.data.get("security_type", "")

        # First check we have a valid network name
        if network_name is None or network_name == "":
            LOG.error("No network name provided")
            return

        # Check if the password is provided if the security type is not open
        if security_type != "open" and secret_phrase is None:
            LOG.error("No password provided")
            self.bus.emit(Message("ovos.phal.nm.connection.failure", {
                          "errorCode": 0, "errorMessage": "Password Required"}))
            return

        # Handle different backends
        if self.backend == "dbus":
            # TODO: Implement dbus backend
            LOG.info("Connecting to network using dbus backend")
        if self.backend == "nmcli":
            connection_process = subprocess.Popen(
                ["nmcli", "device", "wifi", "connect", network_name, "password", secret_phrase], stdout=subprocess.PIPE)
            connection_output = connection_process.communicate()[
                0].decode("utf-8").split("\n")
            if "successfully activated" in connection_output[0]:
                self.bus.emit(Message("ovos.phal.nm.connection.successful", {
                              "connection_name": network_name}))
            else:
                if "(7)" in connection_output[0] or "(10)" in connection_output[0]:
                    self.handle_network_forget_request(Message("ovos.phal.nm.forget", {"connection_name": network_name}))

                self.bus.emit(Message("ovos.phal.nm.connection.failure", {
                              "errorCode": 1, "errorMessage": "Connection Failed"}))

    def handle_open_network_connect_request(self, message):
        network_name = message.data.get("connection_name", "")

        # First check we have a valid network name
        if network_name is None or network_name == "":
            LOG.error("No network name provided")
            return

        # Handle different backends
        if self.backend == "dbus":
            # TODO: Implement dbus backend
            LOG.info("Connecting to network using dbus backend")
        if self.backend == "nmcli":
            connection_process = subprocess.Popen(
                ["nmcli", "device", "wifi", "connect", network_name], stdout=subprocess.PIPE)
            connection_output = connection_process.communicate()[
                0].decode("utf-8").split("\n")
            if "successfully activated" in connection_output[0]:
                self.bus.emit(Message("ovos.phal.nm.connection.successful", {
                              "connection_name": network_name}))
            else:
                self.bus.emit(Message("ovos.phal.nm.connection.failure", {
                              "errorCode": 1, "errorMessage": "Connection Failed"}))

    def handle_network_reconnect_request(self, message):
        network_name = message.data.get("connection_name", "")
        if self.backend == "dbus":
            # TODO: Implement dbus backend
            LOG.info("Connecting to network using dbus backend")
        if self.backend == "nmcli":
            connection_process = subprocess.Popen(
                ["nmcli", "connection", "up", network_name], stdout=subprocess.PIPE)
            connection_output = connection_process.communicate()[
                0].decode("utf-8").split("\n")
            if "successfully activated" in connection_output[0]:
                self.bus.emit(Message("ovos.phal.nm.connection.successful", {
                              "connection_name": network_name}))
            else:
                self.bus.emit(Message("ovos.phal.nm.connection.failure", {
                              "errorCode": 1, "errorMessage": "Connection Failed"}))

    def handle_network_disconnect_request(self, message):
        network_name = message.data.get("connection_name", "")

        # First check we have a valid network name
        if network_name is None or network_name == "":
            LOG.error("No network name provided")
            return

        # Handle different backends
        if self.backend == "dbus":
            # TODO: Implement dbus backend
            LOG.info("Disconnecting from network using dbus backend")
        if self.backend == "nmcli":
            disconnection_process = subprocess.Popen(
                ["nmcli", "connection", "down", network_name], stdout=subprocess.PIPE)
            disconnection_output = disconnection_process.communicate()[
                0].decode("utf-8").split("\n")
            # if disconnection output contains the words "Connection" and "successfully deactivated"
            if "successfully deactivated" in disconnection_output[0]:
                self.bus.emit(Message("ovos.phal.nm.disconnection.successful", {
                              "connection_name": network_name}))
            else:
                self.bus.emit(Message("ovos.phal.nm.disconnection.failure"))

    def handle_network_forget_request(self, message):
        network_name = message.data.get("connection_name", "")

        # First check we have a valid network name
        if network_name is None or network_name == "":
            LOG.error("No network name provided")
            return
        
        # Handle different backends        
        if self.backend == "dbus":
            # TODO: Implement dbus backend
            LOG.info("Forgetting network using dbus backend")
        if self.backend == "nmcli":
            forget_process = subprocess.Popen(
                ["nmcli", "connection", "delete", network_name], stdout=subprocess.PIPE)
            forget_output = forget_process.communicate()[
                0].decode("utf-8").split("\n")
            if "successfully deleted" in forget_output[0]:
                self.bus.emit(Message("ovos.phal.nm.forget.successful",
                              {"connection_name": network_name}))
            else:
                self.bus.emit("ovos.phal.nm.forget.failure")

    def handle_network_connected_query(self, message):
        # Handle Different Backends
        if self.backend == "dbus":
            # TODO: Implement dbus backend
            LOG.info("Checking if network is connected using dbus backend")
        if self.backend == "nmcli":
            connected_process = subprocess.Popen(
                ["nmcli", "connection", "show", "--active"], stdout=subprocess.PIPE)
            connected_output = connected_process.communicate()[
                0].decode("utf-8").split("\n")

            for entry in connected_output:
                if entry == connected_output[0]:
                    continue
                if "wifi" or "ethernet" or "wimax" in connected_output[1]:
                    self.bus.emit(Message("ovos.phal.nm.is.connected", {
                                  "connection_name": connected_output[1].split(" ")[0]}))
                    return

            self.bus.emit(Message("ovos.phal.nm.is.not.connected"))


class DbusNetworkManager:
    # An asyncio based dbus network manager that will handle the scanning, connecting, disconnecting and forgeting of networks
    # This class will be used to handle the dbus backend
    def __init__(self):
        self.wireless_device_path = None

    async def scan_networks(self):
        dbus_bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        introspection = await dbus_bus.introspect('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

        obj = dbus_bus.get_proxy_object(
            "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager", introspection)
        obj_iface = obj.get_interface("org.freedesktop.NetworkManager")
        obj_props = obj.get_interface("org.freedesktop.DBus.Properties")

        devices = await obj_iface.call_get_devices()

        list_of_networks = []

        for device in devices:
            device_obj = dbus_bus.get_proxy_object(
                "org.freedesktop.NetworkManager", device, introspection)
            device_props = device_obj.get_interface(
                "org.freedesktop.DBus.Properties")

            device_type = await device_props.call_get("org.freedesktop.NetworkManager.Device", "DeviceType")

            if device_type.value == 2:
                wifi_device_introspection = await dbus_bus.introspect('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager/Devices')
                wifi_device_obj = dbus_bus.get_proxy_object(
                    "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Devices", wifi_device_introspection)
                local_paths = []
                wireless_object_path = None

                for child_path in wifi_device_obj.child_paths:
                    local_paths.append(child_path)

                for local_path in local_paths:
                    try:
                        local_path_introspection = await dbus_bus.introspect('org.freedesktop.NetworkManager', local_path)
                        local_path_object = dbus_bus.get_proxy_object(
                            "org.freedesktop.NetworkManager", local_path, local_path_introspection)
                        if local_path_object.get_interface("org.freedesktop.NetworkManager.Device.Wireless"):
                            wireless_object_path = local_path
                    except:
                        continue

                if wireless_object_path:
                    self.wireless_device_path = wireless_object_path
                    wireless_object_introspection = await dbus_bus.introspect('org.freedesktop.NetworkManager', wireless_object_path)
                    wireless_object_proxy = dbus_bus.get_proxy_object(
                        "org.freedesktop.NetworkManager", wireless_object_path, wireless_object_introspection)
                    wireless_object_interface = wireless_object_proxy.get_interface(
                        "org.freedesktop.NetworkManager.Device.Wireless")
                    await wireless_object_interface.call_request_scan({})
                    access_points = await wireless_object_interface.call_get_access_points()

                    for access_point in access_points:
                        access_point_introspection = await dbus_bus.introspect('org.freedesktop.NetworkManager', access_point)
                        access_point_proxy = dbus_bus.get_proxy_object(
                            "org.freedesktop.NetworkManager", access_point, access_point_introspection)
                        access_point_interface = access_point_proxy.get_interface(
                            "org.freedesktop.NetworkManager.AccessPoint")

                        access_point_dict = {
                            "access_point_flags": await access_point_interface.get_flags(),
                            "access_point_wpa_flags": await access_point_interface.get_wpa_flags(),
                            "access_point_rsn_flags": await access_point_interface.get_rsn_flags(),
                            "access_point_ssid": await access_point_interface.get_ssid(),
                            "access_point_signal_strength": await access_point_interface.get_strength(),
                            "access_point_connection_path": access_point_interface.path,
                            "access_point_mode": await access_point_interface.get_mode(),
                            "access_point_hw_address": await access_point_interface.get_hw_address()
                        }

                        list_of_networks.append(access_point_dict)

        return list_of_networks
