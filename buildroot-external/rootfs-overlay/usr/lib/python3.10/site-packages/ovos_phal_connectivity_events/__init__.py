import time
from enum import IntEnum

from mycroft_bus_client import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.network_utils import is_connected_dns, is_connected_http


class ConnectivityState(IntEnum):
    """ State of network/internet connectivity.

    See also:
    https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html
    """

    UNKNOWN = 0
    """Network connectivity is unknown."""

    NONE = 1
    """The host is not connected to any network."""

    PORTAL = 2
    """The Internet connection is hijacked by a captive portal gateway."""

    LIMITED = 3
    """The host is connected to a network, does not appear to be able to reach
    the full Internet, but a captive portal has not been detected."""

    FULL = 4
    """The host is connected to a network, and appears to be able to reach the
    full Internet."""


class ConnectivityEvents(PHALPlugin):

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-connectivity-events", config=config)
        self.sleep_time = 60
        self.state = ConnectivityState.UNKNOWN
        self.bus.on("ovos.PHAL.internet_check", self.handle_check)
        self.bus.emit(Message("ovos.PHAL.internet_check"))

    def update_state(self, state, message):
        if state == ConnectivityState.FULL:
            # has internet
            if self.state <= ConnectivityState.NONE:
                self.bus.emit(message.reply("mycroft.network.connected"))
            self.bus.emit(message.reply("mycroft.internet.connected"))
        elif state > ConnectivityState.NONE:
            # connected to network, but no internet)
            if self.state <= ConnectivityState.NONE:
                self.bus.emit(message.reply("mycroft.network.connected"))
            if self.state >= ConnectivityState.FULL:
                self.bus.emit(message.reply("mycroft.internet.disconnected"))
        else:
            # no internet, not connected
            if self.state >= ConnectivityState.FULL:
                self.bus.emit(message.reply("mycroft.internet.disconnected"))
            if self.state >= ConnectivityState.NONE:
                self.bus.emit(message.reply("mycroft.network.disconnected"))
            self.bus.emit(message.reply("enclosure.notify.no_internet"))

        self.state = state
        if self.state == ConnectivityState.FULL:
            self.bus.emit(message.reply("mycroft.internet.state", {"state": "connected"}))
        else:
            self.bus.emit(message.reply("mycroft.internet.state", {"state": "disconnected"}))
        if self.state > ConnectivityState.NONE:
            self.bus.emit(message.reply("mycroft.network.state", {"state": "connected"}))
        else:
            self.bus.emit(message.reply("mycroft.network.state", {"state": "disconnected"}))

    def handle_check(self, message):
        if not is_connected_dns():
            state = ConnectivityState.NONE
        elif not is_connected_http():
            state = ConnectivityState.LIMITED
        else:
            state = ConnectivityState.FULL

        if state != self.state:
            self.update_state(state, message)

        # check again in self.sleep_time
        time.sleep(self.sleep_time)
        self.bus.emit(message)
