# SPDX-FileCopyrightText: Copyright (c) 2022 Kevin Conley
# SPDX-License-Identifier: MIT
"""
`circuitpython_typing.socket`
================================================================================

Type annotation definitions for sockets. Used for `adafruit_requests` and similar libraries.

* Author(s): Kevin Conley
"""

from ssl import SSLContext
from types import ModuleType
from typing import Any, Optional, Tuple, Union

# Protocol was introduced in Python 3.8, TypeAlias in 3.10
from typing_extensions import Protocol, TypeAlias


# Based on https://github.com/python/typeshed/blob/master/stdlib/_socket.pyi

__all__ = [
    # alphabetized
    "CircuitPythonSocketType",
    "CommonCircuitPythonSocketType",
    "CommonSocketType",
    "InterfaceType",
    "LegacyCircuitPythonSocketType",
    "SSLContextType",
    "SocketType",
    "SocketpoolModuleType",
    "StandardPythonSocketType",
    "SupportsRecvInto",
    "SupportsRecvWithFlags",
]


class CommonSocketType(Protocol):
    """Describes the common structure every socket type must have."""

    def send(self, data: bytes, flags: int = ...) -> None:
        """Send data to the socket. The meaning of the optional flags kwarg is
        implementation-specific."""

    def settimeout(self, value: Optional[float]) -> None:
        """Set a timeout on blocking socket operations."""

    def close(self) -> None:
        """Close the socket."""


class CommonCircuitPythonSocketType(CommonSocketType, Protocol):
    """Describes the common structure every CircuitPython socket type must have."""

    def connect(
        self,
        address: Tuple[str, int],
        conntype: Optional[int] = ...,
    ) -> None:
        """Connect to a remote socket at the provided (host, port) address. The conntype
        kwarg optionally may indicate SSL or not, depending on the underlying interface."""


class LegacyCircuitPythonSocketType(CommonCircuitPythonSocketType, Protocol):
    """Describes the structure a legacy CircuitPython socket type must have."""

    def recv(self, bufsize: int = ...) -> bytes:
        """Receive data from the socket. The return value is a bytes object representing
        the data received. The maximum amount of data to be received at once is specified
        by bufsize."""


class SupportsRecvWithFlags(Protocol):
    """Describes a type that posseses a socket recv() method supporting the flags kwarg."""

    def recv(self, bufsize: int = ..., flags: int = ...) -> bytes:
        """Receive data from the socket. The return value is a bytes object representing
        the data received. The maximum amount of data to be received at once is specified
        by bufsize. The meaning of the optional flags kwarg is implementation-specific."""


class SupportsRecvInto(Protocol):
    """Describes a type that possesses a socket recv_into() method."""

    def recv_into(self, buffer: bytearray, nbytes: int = ..., flags: int = ...) -> int:
        """Receive up to nbytes bytes from the socket, storing the data into the provided
        buffer. If nbytes is not specified (or 0), receive up to the size available in the
        given buffer. The meaning of the optional flags kwarg is implementation-specific.
        Returns the number of bytes received."""


class CircuitPythonSocketType(
    CommonCircuitPythonSocketType,
    SupportsRecvInto,
    SupportsRecvWithFlags,
    Protocol,
):  # pylint: disable=too-many-ancestors
    """Describes the structure every modern CircuitPython socket type must have."""


class StandardPythonSocketType(
    CommonSocketType, SupportsRecvInto, SupportsRecvWithFlags, Protocol
):
    """Describes the structure every standard Python socket type must have."""

    def connect(self, address: Union[Tuple[Any, ...], str, bytes]) -> None:
        """Connect to a remote socket at the provided address."""


SocketType: TypeAlias = Union[
    LegacyCircuitPythonSocketType,
    CircuitPythonSocketType,
    StandardPythonSocketType,
]

SocketpoolModuleType = ModuleType


class InterfaceType(Protocol):
    """Describes the structure every interface type must have."""

    @property
    def TLS_MODE(self) -> int:  # pylint: disable=invalid-name
        """Constant representing that a socket's connection mode is TLS."""


SSLContextType: TypeAlias = Union[SSLContext, "_FakeSSLContext"]
