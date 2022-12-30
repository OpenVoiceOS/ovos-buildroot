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

import json
import base64

# Limited maximum tcp packet size to 10 MB;
# Implied by the fact that TCP client aborts the connection once has its packet delivered to server
# thus preventing from sequential traversing
MAX_PACKET_SIZE = 10485760


def get_packet_data(socket, sequentially=False, batch_size=2048) -> bytes:
    """
        Gets all packet data by reading TCP socket stream sequentially
        :@param socket: TCP socket
        :@param sequentially: marker indicating whether received packet data should be read once or sequentially
        :@param batch_size: size of packet added through one sequence

        :@return bytes string representing the received data
    """
    if sequentially:
        fragments = []
        while True:
            chunk = socket.recv(batch_size)
            if not chunk:
                break
            fragments.append(chunk)
        data = b''.join(fragments)
    else:
        data = bytes(socket.recv(MAX_PACKET_SIZE))
    return data


def b64_to_dict(data: bytes, charset: str = "utf-8") -> dict:
    """
        Decodes base64-encoded message to python dictionary
        @param data: string bytes to decode
        @param charset: character set encoding to use (https://docs.python.org/3/library/codecs.html#standard-encodings)

        @return decoded dictionary
    """
    return eval(json.loads(base64.b64decode(data).decode(charset)))


def dict_to_b64(data: dict, charset: str = "utf-8") -> bytes:
    """
        Encodes python dictionary into base64 message
        @param data: python dictionary to encode
        @param charset: character set encoding to use (https://docs.python.org/3/library/codecs.html#standard-encodings)

        @return base64 encoded string
    """
    return base64.b64encode(json.dumps(str(data)).encode(charset))
