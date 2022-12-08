# Copyright 2019 Mycroft AI Inc.
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
"""
The messagebus client is an exteneded websocket connection using a
standard format for the message and handles serialization / deserialization
automatically.
"""
from collections import namedtuple
import json
import logging
import time
import traceback
from threading import Event, Thread

from pyee import ExecutorEventEmitter
from websocket import (WebSocketApp,
                       WebSocketConnectionClosedException,
                       WebSocketException)

from mycroft_bus_client.message import Message
from mycroft_bus_client.util import create_echo_function

LOG = logging.getLogger(__name__)


class MessageWaiter:
    """Wait for a single message.

    Encapsulate the wait for a message logic separating the setup from
    the actual waiting act so the waiting can be setuo, actions can be
    performed and _then_ the message can be waited for.

    Argunments:
        bus: Bus to check for messages on
        message_type: message type to wait for
    """
    def __init__(self, bus, message_type):
        self.bus = bus
        self.msg_type = message_type
        self.received_msg = None
        # Setup response handler
        self.response_event = Event()
        self.bus.once(message_type, self._handler)

    def _handler(self, message):
        """Receive response data."""
        self.received_msg = message
        self.response_event.set()

    def wait(self, timeout=3.0):
        """Wait for message.

        Arguments:
            timeout (int or float): seconds to wait for message

        Returns:
            Message or None
        """
        self.response_event.wait(timeout)
        if not self.response_event.is_set():
            # Clean up the event handler
            try:
                self.bus.remove(self.msg_type, self._handler)
            except (ValueError, KeyError):
                # ValueError occurs on pyee 5.0.1 removing handlers
                # registered with once.
                # KeyError may theoretically occur if the event occurs as
                # the handler is removed
                pass
        return self.received_msg


MessageBusClientConf = namedtuple('MessageBusClientConf',
                                  ['host', 'port', 'route', 'ssl'])


class MessageBusClient:
    """The Mycroft Messagebus Client

    The Messagebus client connects to the Mycroft messagebus service
    and allows communication with the system. It has been extended to work
    like the pyee EventEmitter and tries to offer as much convenience as
    possible to the developer.
    """
    def __init__(self, host='0.0.0.0', port=8181, route='/core', ssl=False,
                 emitter=None):
        self.config = MessageBusClientConf(host, port, route, ssl)
        self.emitter = emitter or ExecutorEventEmitter()
        self.client = self.create_client()
        self.retry = 5
        self.connected_event = Event()
        self.started_running = False

    @staticmethod
    def build_url(host, port, route, ssl):
        """Build a websocket url."""
        return '{scheme}://{host}:{port}{route}'.format(
            scheme='wss' if ssl else 'ws',
            host=host,
            port=str(port),
            route=route)

    def create_client(self):
        """Setup websocket client."""
        url = MessageBusClient.build_url(ssl=self.config.ssl,
                                         host=self.config.host,
                                         port=self.config.port,
                                         route=self.config.route)
        return WebSocketApp(url, on_open=self.on_open, on_close=self.on_close,
                            on_error=self.on_error, on_message=self.on_message)

    def on_open(self, *args):
        """Handle the "open" event from the websocket.

        A Basic message with the name "open" is forwarded to the emitter.
        """
        LOG.info("Connected")
        self.connected_event.set()
        self.emitter.emit("open")
        # Restore reconnect timer to 5 seconds on sucessful connect
        self.retry = 5

    def on_close(self, *args):
        """Handle the "close" event from the websocket.

        A Basic message with the name "close" is forwarded to the emitter.
        """
        self.emitter.emit("close")

    def on_error(self, *args):
        """On error start trying to reconnect to the websocket."""
        if len(args) == 1:
            error = args[0]
        else:
            error = args[1]
        if isinstance(error, WebSocketConnectionClosedException):
            LOG.warning('Could not send message because connection has closed')
        elif isinstance(error, ConnectionRefusedError):
            LOG.warning('Connection Refused. Is Messagebus Service running?')
        else:
            LOG.exception('=== %s ===', repr(error))

        try:
            self.emitter.emit('error', error)
            if self.client.keep_running:
                self.client.close()
        except Exception as e:
            LOG.error('Exception closing websocket: %s', repr(e))

        LOG.warning("Message Bus Client "
                    "will reconnect in %.1f seconds.", self.retry)
        time.sleep(self.retry)
        self.retry = min(self.retry * 2, 60)
        try:
            self.emitter.emit('reconnecting')
            self.client = self.create_client()
            self.run_forever()
        except WebSocketException:
            pass

    def on_message(self, *args):
        """Handle incoming websocket message.

        Args:
            message (str): serialized Mycroft Message
        """
        if len(args) == 1:
            message = args[0]
        else:
            message = args[1]
        parsed_message = Message.deserialize(message)
        self.emitter.emit('message', message)
        self.emitter.emit(parsed_message.msg_type, parsed_message)

    def emit(self, message):
        """Send a message onto the message bus.

        This will both send the message to the local process using the
        event emitter and onto the Mycroft websocket for other processes.

        Args:
            message (Message): Message to send
        """
        if not self.connected_event.wait(10):
            if not self.started_running:
                raise ValueError('You must execute run_forever() '
                                 'before emitting messages')
            self.connected_event.wait()

        try:
            if hasattr(message, 'serialize'):
                self.client.send(message.serialize())
            else:
                self.client.send(json.dumps(message.__dict__))
        except WebSocketConnectionClosedException:
            LOG.warning('Could not send %s message because connection '
                        'has been closed', message.msg_type)

    def wait_for_message(self, message_type, timeout=3.0):
        """Wait for a message of a specific type.

        Arguments:
            message_type (str): the message type of the expected message
            timeout: seconds to wait before timeout, defaults to 3

        Returns:
            The received message or None if the response timed out
        """

        return MessageWaiter(self, message_type).wait(timeout)

    def wait_for_response(self, message, reply_type=None, timeout=3.0):
        """Send a message and wait for a response.

        Arguments:
            message (Message): message to send
            reply_type (str): the message type of the expected reply.
                              Defaults to "<message.msg_type>.response".
            timeout: seconds to wait before timeout, defaults to 3

        Returns:
            The received message or None if the response timed out
        """
        message_type = reply_type or message.msg_type + '.response'
        waiter = MessageWaiter(self, message_type)  # Setup response handler
        # Send message and wait for it's response
        self.emit(message)
        return waiter.wait(timeout)

    def on(self, event_name, func):
        """Register callback with event emitter.

        Args:
            event_name (str): message type to map to the callback
            func (callable): callback function
        """
        self.emitter.on(event_name, func)

    def once(self, event_name, func):
        """Register callback with event emitter for a single call.

        Args:
            event_name (str): message type to map to the callback
            func (callable): callback function
        """
        self.emitter.once(event_name, func)

    def remove(self, event_name, func):
        """Remove registered event.

        Args:
            event_name (str): message type to map to the callback
            func (callable): callback function
        """
        try:
            if event_name not in self.emitter._events:
                LOG.debug("Not able to find '%s'", event_name)
            self.emitter.remove_listener(event_name, func)
        except ValueError:
            LOG.warning('Failed to remove event %s: %s',
                        event_name, str(func))
            for line in traceback.format_stack():
                LOG.warning(line.strip())

            if event_name not in self.emitter._events:
                LOG.debug("Not able to find '%s'", event_name)
            LOG.warning("Existing events: %s", repr(self.emitter._events))
            for evt in self.emitter._events:
                LOG.warning("   %s", repr(evt))
                LOG.warning("       %s", repr(self.emitter._events[evt]))
            if event_name in self.emitter._events:
                LOG.debug("Removing found '%s'", event_name)
            else:
                LOG.debug("Not able to find '%s'", event_name)
            LOG.warning('----- End dump -----')

    def remove_all_listeners(self, event_name):
        """Remove all listeners connected to event_name.

            Arguments:
                event_name: event from which to remove listeners
        """
        if event_name is None:
            raise ValueError
        self.emitter.remove_all_listeners(event_name)

    def run_forever(self):
        """Start the websocket handling."""
        self.started_running = True
        self.client.run_forever()

    def close(self):
        """Close the websocket connection."""
        self.client.close()
        self.connected_event.clear()

    def run_in_thread(self):
        """Launches the run_forever in a separate daemon thread."""
        t = Thread(target=self.run_forever)
        t.daemon = True
        t.start()
        return t


def echo():
    """Echo function repeating all input from a user."""
    message_bus_client = MessageBusClient()

    def repeat_utterance(message):
        message.msg_type = 'speak'
        message_bus_client.emit(message)

    message_bus_client.on('message', create_echo_function(None))
    message_bus_client.on('recognizer_loop:utterance', repeat_utterance)
    message_bus_client.run_forever()


if __name__ == "__main__":
    echo()
