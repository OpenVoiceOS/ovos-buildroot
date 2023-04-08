# Copyright 2021 Mycroft AI Inc.
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

from queue import Queue
from threading import Lock, Event
from uuid import uuid4
import time


class MessageCollector:
    """Collect multiple response.

    This class encapsulates the logic for collecting messages from
    multiple handlers returning the list of all answers.

    Argunments:
        bus: Bus to check for messages on
        message (Message): message to send
        min_timeout (int/float): Minimum time to wait for a response
        max_timeout (int/float): Maximum allowed time to wait for an answer
        direct_return_func (callable): Optional function for allowing an
            early return (not all registered handlers need to respond)
    """
    def __init__(self, bus, message,
                 min_timeout, max_timeout,
                 direct_return_func=None):
        self.lock = Lock()
        self.bus = bus
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        self.direct_return_func = direct_return_func or (lambda msg: False)

        # Create an unique id for the collection
        self.collect_id = str(uuid4())
        self.handlers = {}
        self.responses = {}
        self.all_collected = Event()
        self.message = message
        self.message.context['__collect_id__'] = self.collect_id
        self._start_time = 0

        self.on_response_callback = None
        self.queue = Queue()

    def __iter__(self):
        return self

    def __next__(self):
        msg = Queue.get()
        if msg is not None:
            return msg
        else:
            raise StopIteration

    def on_response(self, callback_func):
        self.on_response_callback = callback_func

    def _register_handler(self, msg):
        """Handler for registration of collection handler.

        Args:
            msg: Message from handler.
        """
        handler_id = msg.data['handler']
        timeout = msg.data['timeout']
        with self.lock:
            if (msg.data['query'] == self.collect_id and
                    handler_id not in self.handlers):
                previous_timeout = self.handlers.get(handler_id, 0)
                self.handlers[handler_id] = previous_timeout + timeout

    def _receive_response(self, msg):
        """Handler for capturing final response from a handler.

        Args:
            msg: Message with collect handler's response.
        """
        with self.lock:
            if msg.data['query'] == self.collect_id:
                self.queue.put(msg)
                self.responses[msg.data['handler']] = msg
                self.handlers[msg.data['handler']] = 0  # Reset timeout
                # If all registered handlers have responded with an answer
                # or a VERY good answer has been found indicate end of wait.
                all_collected = len(self.responses) == len(self.handlers)
                if (all_collected or self.direct_return_func(msg)):
                    self.queue.put(None)
                    self.all_collected.set()

        if self.on_response_callback:
            self.on_response_callback(msg)

    def _setup_collection_handlers(self):
        """Create messages for handling and responses."""
        base_msg_type = self.message.msg_type
        self.bus.on(base_msg_type + '.handling', self._register_handler)
        self.bus.on(base_msg_type + '.response', self._receive_response)

    def _teardown_collection_handlers(self):
        """Remove all registered handlers for response collection."""
        base_msg_type = self.message.msg_type
        self.bus.remove(base_msg_type + '.handling', self._register_handler)
        self.bus.remove(base_msg_type + '.response', self._receive_response)

    def start(self):
        """Send collection request.

        Register handler to capture handlers trying to provide answer.
        """
        self._setup_collection_handlers()
        self.bus.emit(self.message)
        self.start_time = time.monotonic()

        time.sleep(self.min_timeout)

    def collect(self):
        """Emit message and wait for handlers to finish."""
        self.start()
        if len(self.handlers) == 0:
            # No handlers has registered to answer the query
            result = []
        else:
            result = self._wait_for_registered_handlers()

        self.shutdown()
        return result

    def wait(self):
        """Wait for timeout or for all handlers to respond."""
        self._wait_for_registered_handlers()

    def _wait_for_registered_handlers(self):
        """
        Wait until all handlers have sent a response or the timeout is reached.
        """
        # Reset the all_collected event if needed.
        # May be set if the first registered message replies immediately before
        # any other handlers has registered.
        # TODO: check early return criteria
        with self.lock:
            all_collected = len(self.responses) == len(self.handlers)
            if not all_collected:
                self.all_collected.clear()

        # Wait until all handlers have responded or timeout is reached
        time_waited = self.min_timeout
        remaining_timeout = max(self.handlers.values()) - time_waited
        while remaining_timeout > 0.0 and time_waited < self.max_timeout:
            if self.all_collected.wait(timeout=0.1):
                break

            time_waited += 0.1
            remaining_timeout = max(self.handlers.values()) - time_waited

        self.queue.put(None)
        return [self.responses[key] for key in self.responses]

    def shutdown(self):
        """Shutdown the object, stop waiting for further responses."""
        self._teardown_collection_handlers()
        if self.on_response_callback:
            self.on_response_callback = None
