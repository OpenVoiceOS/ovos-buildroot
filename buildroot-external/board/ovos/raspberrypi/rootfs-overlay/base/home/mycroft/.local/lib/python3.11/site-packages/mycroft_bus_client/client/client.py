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
from uuid import uuid4

from pyee import ExecutorEventEmitter
from websocket import (WebSocketApp,
                       WebSocketConnectionClosedException,
                       WebSocketException)

from mycroft_bus_client.message import Message, CollectionMessage
from mycroft_bus_client.util import create_echo_function

from .collector import MessageCollector
from .waiter import MessageWaiter

LOG = logging.getLogger(__name__)


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
        self.wrapped_funcs = {}

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
            LOG.error(f'Exception closing websocket at {self.client.url}: {e}')

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

    def collect_responses(self, message,
                          min_timeout=0.2, max_timeout=3.0,
                          direct_return_func=lambda msg: False):
        """Collect responses from multiple handlers.

        This sets up a collect-call (pun intended) expecting multiple handlers
        to respond.

        Args:
            message (Message): message to send
            min_timeout (int/float): Minimum time to wait for a response
            max_timeout (int/float): Maximum allowed time to wait for an answer
            direct_return_func (callable): Optional function for allowing an
                early return (not all registered handlers need to respond)

            Returns:
                (list) collected response messages.
        """
        collector = MessageCollector(self, message,
                                     min_timeout, max_timeout,
                                     direct_return_func)
        return collector.collect()

    def on_collect(self, event_name, func, timeout=2):
        """Create a handler for a collect_responses call.

        This immeditely responds with an ack to register the handler with
        the caller, promising to return a response.

        The handler function then needs to send a response.

        Args:
            event_name (str): Message type to listen for.
            func (callable): function / method do be called for processing the
                             message.
            timeout (int/float): optional timeout of the handler
        """
        def wrapper(msg):
            collect_id = msg.context['__collect_id__']
            handler_id = str(uuid4())
            # Immediately respond that something is working on the issue
            acknowledge = msg.reply(msg.msg_type + '.handling',
                                    data={'query': collect_id,
                                          'handler': handler_id,
                                          'timeout': timeout})
            self.emit(acknowledge)
            func(CollectionMessage.from_message(msg, handler_id, collect_id))
        self.wrapped_funcs[func] = wrapper
        self.on(event_name, wrapper)

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
        if func in self.wrapped_funcs:
            self._remove_wrapped(event_name, func)
        else:
            self._remove_normal(event_name, func)

    def _remove_wrapped(self, event_name, external_func):
        """Remove a wrapped function."""

        wrapper = self.wrapped_funcs.pop(external_func)
        self._remove_normal(event_name, wrapper)

    def _remove_normal(self, event_name, func):
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
