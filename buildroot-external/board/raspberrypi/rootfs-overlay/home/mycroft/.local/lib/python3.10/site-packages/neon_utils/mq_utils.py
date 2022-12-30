# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import uuid

try:
    from threading import Event
    from pika.channel import Channel
    from pika.exceptions import ProbableAccessDeniedError, StreamLostError
    from neon_mq_connector.connector import MQConnector
    from ovos_config.config import Configuration
except ImportError:
    raise ImportError("MQ dependencies not available,"
                      " pip install neon-utils[network]")

from neon_utils.logger import LOG
from neon_utils.socket_utils import b64_to_dict

logging.getLogger("pika").setLevel(logging.CRITICAL)

_default_mq_config = {
    "server": "api.neon.ai",
    "port": 5672,
    "users": {
        "mq_handler": {
            "user": 'neon_api_utils',
            "password": 'Klatchat2021'
        }
    }
}


class NeonMQHandler(MQConnector):
    def __init__(self, config: dict, service_name: str, vhost: str):
        super().__init__(config, service_name)
        self.vhost = vhost
        import pika
        self.connection = pika.BlockingConnection(
            parameters=self.get_connection_params(vhost))


def get_mq_response(vhost: str, request_data: dict, target_queue: str,
                    response_queue: str = None, timeout: int = 30) -> dict:
    # TODO: Remove in v1.0.0 DM
    LOG.warning(f"This method has been deprecated, please use: `send_mq_request`")
    return send_mq_request(vhost, request_data, target_queue, response_queue, timeout, True)


def send_mq_request(vhost: str, request_data: dict, target_queue: str,
                    response_queue: str = None, timeout: int = 30, expect_response: bool = True) -> dict:
    """
    Sends a request to the MQ server and returns the response.
    :param vhost: vhost to target
    :param request_data: data to post to target_queue
    :param target_queue: queue to post request to
    :param response_queue: optional queue to monitor for a response. Generally should be blank
    :param timeout: time in seconds to wait for a response before timing out
    :param expect_response: boolean indicating whether or not a response is expected
    :return: response to request
    """
    response_queue = response_queue or uuid.uuid4().hex

    response_event = Event()
    message_id = None
    response_data = dict()
    config = dict()

    def on_error(thread, error):
        """
        Override default error handler to suppress certain logged errors.
        """
        if isinstance(error, StreamLostError):
            return
        LOG.error(f"{thread} raised {error}")

    def handle_mq_response(channel: Channel, method, _, body):
        """
            Method that handles Neon API output.
            In case received output message with the desired id, event stops
        """
        api_output = b64_to_dict(body)
        api_output_msg_id = api_output.get('message_id', None)
        if api_output_msg_id == message_id:
            LOG.debug(f'MQ output: {api_output}')
            channel.basic_ack(delivery_tag=method.delivery_tag)
            channel.close()
            response_data.update(api_output)
            response_event.set()
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag)
            LOG.debug(f"Ignoring {api_output_msg_id} waiting for {message_id}")

    try:
        # LOG.debug('Creating Neon MQ Handler Instance...')
        config = dict(Configuration()).get('MQ') or _default_mq_config
        # LOG.info(f"MQ Config={config}")
        neon_api_mq_handler = NeonMQHandler(config=config, service_name='mq_handler', vhost=vhost)
        # LOG.debug(f'Established MQ connection: {neon_api_mq_handler.connection}')
        if not neon_api_mq_handler.connection.is_open:
            raise ConnectionError("MQ Connection not established.")

        if expect_response:
            neon_api_mq_handler.register_consumer('neon_output_handler',
                                                  neon_api_mq_handler.vhost, response_queue,
                                                  handle_mq_response, on_error, auto_ack=False)
            neon_api_mq_handler.run_consumers()
            request_data['routing_key'] = response_queue

        message_id = neon_api_mq_handler.emit_mq_message(connection=neon_api_mq_handler.connection,
                                                         queue=target_queue,
                                                         request_data=request_data,
                                                         exchange='')
        LOG.debug(f'Sent request with keys: {request_data.keys()}')

        if expect_response:
            response_event.wait(timeout)
            if not response_event.is_set():
                LOG.error(f"Timeout waiting for response to: {message_id} on {response_queue}")
            neon_api_mq_handler.stop_consumers()
    except ProbableAccessDeniedError:
        raise ValueError(f"{vhost} is not a valid endpoint for {config.get('users').get('mq_handler').get('user')}")
    except Exception as ex:
        LOG.error(f'Exception occurred while resolving Neon API: {ex}')
    return response_data
