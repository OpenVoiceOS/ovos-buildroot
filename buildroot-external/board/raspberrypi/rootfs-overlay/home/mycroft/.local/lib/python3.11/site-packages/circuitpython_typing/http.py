# SPDX-FileCopyrightText: Copyright (c) 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""
`circuitpython_typing.http`
===========================

Type annotation definitions for HTTP and related objects

* Author(s): Alec Delaney
"""

# Protocol was introduced in Python 3.8.
from typing_extensions import Protocol
from adafruit_requests import Response


class HTTPProtocol(Protocol):
    """Protocol for HTTP request managers, like typical wifi managers"""

    def get(self, url: str, **kw) -> Response:
        """Send HTTP GET request"""

    def put(self, url: str, **kw) -> Response:
        """Send HTTP PUT request"""

    def post(self, url: str, **kw) -> Response:
        """Send HTTP POST request"""

    def patch(self, url: str, **kw) -> Response:
        """Send HTTP PATCH request"""

    def delete(self, url: str, **kw) -> Response:
        """Send HTTP DELETE request"""
