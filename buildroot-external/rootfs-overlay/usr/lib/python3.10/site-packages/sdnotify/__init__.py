import socket
import os
import sys

__version__ = "0.3.2"

# Byte conversion utility for compatibility between
# Python 2 and 3.
# http://python3porting.com/problems.html#nicer-solutions
if sys.version_info < (3,):
    def _b(x):
        return x
else:
    import codecs
    def _b(x):
        return codecs.latin_1_encode(x)[0]


class SystemdNotifier:
    """This class holds a connection to the systemd notification socket
    and can be used to send messages to systemd using its notify method."""

    def __init__(self, debug=False):
        """Instantiate a new notifier object. This will initiate a connection
        to the systemd notification socket.

        Normally this method silently ignores exceptions (for example, if the
        systemd notification socket is not available) to allow applications to
        function on non-systemd based systems. However, setting debug=True will
        cause this method to raise any exceptions generated to the caller, to
        aid in debugging.
        """
        self.debug = debug
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            addr = os.getenv('NOTIFY_SOCKET')
            if addr[0] == '@':
                addr = '\0' + addr[1:]
            self.socket.connect(addr)
        except:
            self.socket = None
            if self.debug:
                raise

    def notify(self, state):
        """Send a notification to systemd. state is a string; see
        the man page of sd_notify (http://www.freedesktop.org/software/systemd/man/sd_notify.html)
        for a description of the allowable values.

        Normally this method silently ignores exceptions (for example, if the
        systemd notification socket is not available) to allow applications to
        function on non-systemd based systems. However, setting debug=True will
        cause this method to raise any exceptions generated to the caller, to
        aid in debugging."""
        try:
            self.socket.sendall(_b(state))
        except:
            if self.debug:
                raise
