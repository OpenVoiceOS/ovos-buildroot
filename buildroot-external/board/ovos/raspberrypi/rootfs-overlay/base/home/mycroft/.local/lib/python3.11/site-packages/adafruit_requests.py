# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-FileCopyrightText: 2020 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_requests`
================================================================================

A requests-like library for web interfacing


* Author(s): ladyada, Paul Sokolovsky, Scott Shawcroft

Implementation Notes
--------------------

Adapted from https://github.com/micropython/micropython-lib/tree/master/urequests

micropython-lib consists of multiple modules from different sources and
authors. Each module comes under its own licensing terms. Short name of
a license can be found in a file within a module directory (usually
metadata.txt or setup.py). Complete text of each license used is provided
at https://github.com/micropython/micropython-lib/blob/master/LICENSE

author='Paul Sokolovsky'
license='MIT'

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

__version__ = "1.12.11"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Requests.git"

import errno
import sys

import json as json_module

if sys.implementation.name == "circuitpython":

    def cast(_t, value):
        """No-op shim for the typing.cast() function which is not available in CircuitPython."""
        return value

else:
    from ssl import SSLContext
    from types import ModuleType, TracebackType
    from typing import Any, Dict, Optional, Tuple, Type, Union, cast

    try:
        from typing import Protocol
    except ImportError:
        from typing_extensions import Protocol

    # Based on https://github.com/python/typeshed/blob/master/stdlib/_socket.pyi
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

        def recv_into(
            self, buffer: bytearray, nbytes: int = ..., flags: int = ...
        ) -> int:
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

    SocketType = Union[
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

    SSLContextType = Union[SSLContext, "_FakeSSLContext"]


class _RawResponse:
    def __init__(self, response: "Response") -> None:
        self._response = response

    def read(self, size: int = -1) -> bytes:
        """Read as much as available or up to size and return it in a byte string.

        Do NOT use this unless you really need to. Reusing memory with `readinto` is much better.
        """
        if size == -1:
            return self._response.content
        return self._response.socket.recv(size)

    def readinto(self, buf: bytearray) -> int:
        """Read as much as available into buf or until it is full. Returns the number of bytes read
        into buf."""
        return self._response._readinto(buf)  # pylint: disable=protected-access


class OutOfRetries(Exception):
    """Raised when requests has retried to make a request unsuccessfully."""


class Response:
    """The response from a request, contains all the headers/content"""

    # pylint: disable=too-many-instance-attributes

    encoding = None

    def __init__(self, sock: SocketType, session: Optional["Session"] = None) -> None:
        self.socket = sock
        self.encoding = "utf-8"
        self._cached = None
        self._headers = {}

        # _start_index and _receive_buffer are used when parsing headers.
        # _receive_buffer will grow by 32 bytes everytime it is too small.
        self._received_length = 0
        self._receive_buffer = bytearray(32)
        self._remaining = None
        self._chunked = False

        self._backwards_compatible = not hasattr(sock, "recv_into")

        http = self._readto(b" ")
        if not http:
            if session:
                session._close_socket(self.socket)
            else:
                self.socket.close()
            raise RuntimeError("Unable to read HTTP response.")
        self.status_code = int(bytes(self._readto(b" ")))
        self.reason = self._readto(b"\r\n")
        self._parse_headers()
        self._raw = None
        self._session = session

    def __enter__(self) -> "Response":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[type]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def _recv_into(self, buf: bytearray, size: int = 0) -> int:
        if self._backwards_compatible:
            size = len(buf) if size == 0 else size
            b = self.socket.recv(size)
            read_size = len(b)
            buf[:read_size] = b
            return read_size
        return cast("SupportsRecvInto", self.socket).recv_into(buf, size)

    def _readto(self, stop: bytes) -> bytearray:
        buf = self._receive_buffer
        end = self._received_length
        while True:
            i = buf.find(stop, 0, end)
            if i >= 0:
                # Stop was found. Return everything up to but not including stop.
                result = buf[:i]
                new_start = i + len(stop)
                # Remove everything up to and including stop from the buffer.
                new_end = end - new_start
                buf[:new_end] = buf[new_start:end]
                self._received_length = new_end
                return result

            # Not found so load more bytes.
            # If our buffer is full, then make it bigger to load more.
            if end == len(buf):
                new_buf = bytearray(len(buf) + 32)
                new_buf[: len(buf)] = buf
                buf = new_buf
                self._receive_buffer = buf

            read = self._recv_into(memoryview(buf)[end:])
            if read == 0:
                self._received_length = 0
                return buf[:end]
            end += read

    def _read_from_buffer(
        self, buf: Optional[bytearray] = None, nbytes: Optional[int] = None
    ) -> int:
        if self._received_length == 0:
            return 0
        read = self._received_length
        if nbytes < read:
            read = nbytes
        membuf = memoryview(self._receive_buffer)
        if buf:
            buf[:read] = membuf[:read]
        if read < self._received_length:
            new_end = self._received_length - read
            self._receive_buffer[:new_end] = membuf[read : self._received_length]
            self._received_length = new_end
        else:
            self._received_length = 0
        return read

    def _readinto(self, buf: bytearray) -> int:
        if not self.socket:
            raise RuntimeError(
                "Newer Response closed this one. Use Responses immediately."
            )

        if not self._remaining:
            # Consume the chunk header if need be.
            if self._chunked:
                # Consume trailing \r\n for chunks 2+
                if self._remaining == 0:
                    self._throw_away(2)
                chunk_header = bytes(self._readto(b"\r\n")).split(b";", 1)[0]
                http_chunk_size = int(bytes(chunk_header), 16)
                if http_chunk_size == 0:
                    self._chunked = False
                    self._parse_headers()
                    return 0
                self._remaining = http_chunk_size
            else:
                return 0

        nbytes = len(buf)
        if nbytes > self._remaining:
            nbytes = self._remaining

        read = self._read_from_buffer(buf, nbytes)
        if read == 0:
            read = self._recv_into(buf, nbytes)
        self._remaining -= read

        return read

    def _throw_away(self, nbytes: int) -> None:
        nbytes -= self._read_from_buffer(nbytes=nbytes)

        buf = self._receive_buffer
        len_buf = len(buf)
        for _ in range(nbytes // len_buf):
            to_read = len_buf
            while to_read > 0:
                to_read -= self._recv_into(buf, to_read)
        to_read = nbytes % len_buf
        while to_read > 0:
            to_read -= self._recv_into(buf, to_read)

    def close(self) -> None:
        """Drain the remaining ESP socket buffers. We assume we already got what we wanted."""
        if not self.socket:
            return
        # Make sure we've read all of our response.
        if self._cached is None:
            if self._remaining and self._remaining > 0:
                self._throw_away(self._remaining)
            elif self._chunked:
                while True:
                    chunk_header = bytes(self._readto(b"\r\n")).split(b";", 1)[0]
                    chunk_size = int(bytes(chunk_header), 16)
                    if chunk_size == 0:
                        break
                    self._throw_away(chunk_size + 2)
                self._parse_headers()
        if self._session:
            self._session._free_socket(self.socket)  # pylint: disable=protected-access
        else:
            self.socket.close()
        self.socket = None

    def _parse_headers(self) -> None:
        """
        Parses the header portion of an HTTP request/response from the socket.
        Expects first line of HTTP request/response to have been read already.
        """
        while True:
            header = self._readto(b"\r\n")
            if not header:
                break
            title, content = bytes(header).split(b": ", 1)
            if title and content:
                # enforce that all headers are lowercase
                title = str(title, "utf-8").lower()
                content = str(content, "utf-8")
                if title == "content-length":
                    self._remaining = int(content)
                if title == "transfer-encoding":
                    self._chunked = content.strip().lower() == "chunked"
                if title == "set-cookie" and title in self._headers:
                    self._headers[title] += ", " + content
                else:
                    self._headers[title] = content

    def _validate_not_gzip(self) -> None:
        """gzip encoding is not supported. Raise an exception if found."""
        if (
            "content-encoding" in self.headers
            and self.headers["content-encoding"] == "gzip"
        ):
            raise ValueError(
                "Content-encoding is gzip, data cannot be accessed as json or text. "
                "Use content property to access raw bytes."
            )

    @property
    def headers(self) -> Dict[str, str]:
        """
        The response headers. Does not include headers from the trailer until
        the content has been read.
        """
        return self._headers

    @property
    def content(self) -> bytes:
        """The HTTP content direct from the socket, as bytes"""
        if self._cached is not None:
            if isinstance(self._cached, bytes):
                return self._cached
            raise RuntimeError("Cannot access content after getting text or json")

        self._cached = b"".join(self.iter_content(chunk_size=32))
        return self._cached

    @property
    def text(self) -> str:
        """The HTTP content, encoded into a string according to the HTTP
        header encoding"""
        if self._cached is not None:
            if isinstance(self._cached, str):
                return self._cached
            raise RuntimeError("Cannot access text after getting content or json")

        self._validate_not_gzip()

        self._cached = str(self.content, self.encoding)
        return self._cached

    def json(self) -> Any:
        """The HTTP content, parsed into a json dictionary"""
        # The cached JSON will be a list or dictionary.
        if self._cached:
            if isinstance(self._cached, (list, dict)):
                return self._cached
            raise RuntimeError("Cannot access json after getting text or content")
        if not self._raw:
            self._raw = _RawResponse(self)

        self._validate_not_gzip()

        obj = json_module.load(self._raw)
        if not self._cached:
            self._cached = obj
        self.close()
        return obj

    def iter_content(self, chunk_size: int = 1, decode_unicode: bool = False) -> bytes:
        """An iterator that will stream data by only reading 'chunk_size'
        bytes and yielding them, when we can't buffer the whole datastream"""
        if decode_unicode:
            raise NotImplementedError("Unicode not supported")

        b = bytearray(chunk_size)
        while True:
            size = self._readinto(b)
            if size == 0:
                break
            if size < chunk_size:
                chunk = bytes(memoryview(b)[:size])
            else:
                chunk = bytes(b)
            yield chunk
        self.close()


class Session:
    """HTTP session that shares sockets and ssl context."""

    def __init__(
        self,
        socket_pool: SocketpoolModuleType,
        ssl_context: Optional[SSLContextType] = None,
    ) -> None:
        self._socket_pool = socket_pool
        self._ssl_context = ssl_context
        # Hang onto open sockets so that we can reuse them.
        self._open_sockets = {}
        self._socket_free = {}
        self._last_response = None

    def _free_socket(self, socket: SocketType) -> None:
        if socket not in self._open_sockets.values():
            raise RuntimeError("Socket not from session")
        self._socket_free[socket] = True

    def _close_socket(self, sock: SocketType) -> None:
        sock.close()
        del self._socket_free[sock]
        key = None
        for k in self._open_sockets:  # pylint: disable=consider-using-dict-items
            if self._open_sockets[k] == sock:
                key = k
                break
        if key:
            del self._open_sockets[key]

    def _free_sockets(self) -> None:
        free_sockets = []
        for sock, val in self._socket_free.items():
            if val:
                free_sockets.append(sock)
        for sock in free_sockets:
            self._close_socket(sock)

    def _get_socket(
        self, host: str, port: int, proto: str, *, timeout: float = 1
    ) -> CircuitPythonSocketType:
        # pylint: disable=too-many-branches
        key = (host, port, proto)
        if key in self._open_sockets:
            sock = self._open_sockets[key]
            if self._socket_free[sock]:
                self._socket_free[sock] = False
                return sock
        if proto == "https:" and not self._ssl_context:
            raise RuntimeError(
                "ssl_context must be set before using adafruit_requests for https"
            )
        addr_info = self._socket_pool.getaddrinfo(
            host, port, 0, self._socket_pool.SOCK_STREAM
        )[0]
        retry_count = 0
        sock = None
        while retry_count < 5 and sock is None:
            if retry_count > 0:
                if any(self._socket_free.items()):
                    self._free_sockets()
                else:
                    raise RuntimeError("Sending request failed")
            retry_count += 1

            try:
                sock = self._socket_pool.socket(addr_info[0], addr_info[1])
            except OSError:
                continue
            except RuntimeError:
                continue

            connect_host = addr_info[-1][0]
            if proto == "https:":
                sock = self._ssl_context.wrap_socket(sock, server_hostname=host)
                connect_host = host
            sock.settimeout(timeout)  # socket read timeout

            try:
                sock.connect((connect_host, port))
            except MemoryError:
                sock.close()
                sock = None
            except OSError:
                sock.close()
                sock = None

        if sock is None:
            raise RuntimeError("Repeated socket failures")

        self._open_sockets[key] = sock
        self._socket_free[sock] = False
        return sock

    @staticmethod
    def _send(socket: SocketType, data: bytes):
        total_sent = 0
        while total_sent < len(data):
            # ESP32SPI sockets raise a RuntimeError when unable to send.
            try:
                sent = socket.send(data[total_sent:])
            except OSError as exc:
                if exc.errno == errno.EAGAIN:
                    # Can't send right now (e.g., no buffer space), try again.
                    continue
                # Some worse error.
                raise
            except RuntimeError as exc:
                raise OSError(errno.EIO) from exc
            if sent is None:
                sent = len(data)
            if sent == 0:
                # Not EAGAIN; that was already handled.
                raise OSError(errno.EIO)
            total_sent += sent

    def _send_request(
        self,
        socket: SocketType,
        host: str,
        method: str,
        path: str,
        headers: Dict[str, str],
        data: Any,
        json: Any,
    ):
        # pylint: disable=too-many-arguments
        self._send(socket, bytes(method, "utf-8"))
        self._send(socket, b" /")
        self._send(socket, bytes(path, "utf-8"))
        self._send(socket, b" HTTP/1.1\r\n")
        if "Host" not in headers:
            self._send(socket, b"Host: ")
            self._send(socket, bytes(host, "utf-8"))
            self._send(socket, b"\r\n")
        if "User-Agent" not in headers:
            self._send(socket, b"User-Agent: Adafruit CircuitPython\r\n")
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            self._send(socket, k.encode())
            self._send(socket, b": ")
            self._send(socket, headers[k].encode())
            self._send(socket, b"\r\n")
        if json is not None:
            assert data is None
            data = json_module.dumps(json)
            self._send(socket, b"Content-Type: application/json\r\n")
        if data:
            if isinstance(data, dict):
                self._send(
                    socket, b"Content-Type: application/x-www-form-urlencoded\r\n"
                )
                _post_data = ""
                for k in data:
                    _post_data = "{}&{}={}".format(_post_data, k, data[k])
                data = _post_data[1:]
            if isinstance(data, str):
                data = bytes(data, "utf-8")
            self._send(socket, b"Content-Length: %d\r\n" % len(data))
        self._send(socket, b"\r\n")
        if data:
            self._send(socket, bytes(data))

    # pylint: disable=too-many-branches, too-many-statements, unused-argument, too-many-arguments, too-many-locals
    def request(
        self,
        method: str,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
        timeout: float = 60,
    ) -> Response:
        """Perform an HTTP request to the given url which we will parse to determine
        whether to use SSL ('https://') or not. We can also send some provided 'data'
        or a json dictionary which we will stringify. 'headers' is optional HTTP headers
        sent along. 'stream' will determine if we buffer everything, or whether to only
        read only when requested
        """
        if not headers:
            headers = {}

        try:
            proto, dummy, host, path = url.split("/", 3)
            # replace spaces in path
            path = path.replace(" ", "%20")
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""
        if proto == "http:":
            port = 80
        elif proto == "https:":
            port = 443
        else:
            raise ValueError("Unsupported protocol: " + proto)

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        if self._last_response:
            self._last_response.close()
            self._last_response = None

        # We may fail to send the request if the socket we got is closed already. So, try a second
        # time in that case.
        retry_count = 0
        while retry_count < 2:
            retry_count += 1
            socket = self._get_socket(host, port, proto, timeout=timeout)
            ok = True
            try:
                self._send_request(socket, host, method, path, headers, data, json)
            except OSError:
                ok = False
            if ok:
                # Read the H of "HTTP/1.1" to make sure the socket is alive. send can appear to work
                # even when the socket is closed.
                if hasattr(socket, "recv"):
                    result = socket.recv(1)
                else:
                    result = bytearray(1)
                    try:
                        socket.recv_into(result)
                    except OSError:
                        pass
                if result == b"H":
                    # Things seem to be ok so break with socket set.
                    break
            self._close_socket(socket)
            socket = None

        if not socket:
            raise OutOfRetries("Repeated socket failures")

        resp = Response(socket, self)  # our response
        if "location" in resp.headers and 300 <= resp.status_code <= 399:
            # a naive handler for redirects
            redirect = resp.headers["location"]

            if redirect.startswith("http"):
                # absolute URL
                url = redirect
            elif redirect[0] == "/":
                # relative URL, absolute path
                url = "/".join([proto, dummy, host, redirect[1:]])
            else:
                # relative URL, relative path
                path = path.rsplit("/", 1)[0]

                while redirect.startswith("../"):
                    path = path.rsplit("/", 1)[0]
                    redirect = redirect.split("../", 1)[1]

                url = "/".join([proto, dummy, host, path, redirect])

            self._last_response = resp
            resp = self.request(method, url, data, json, headers, stream, timeout)

        self._last_response = resp
        return resp

    def head(self, url: str, **kw) -> Response:
        """Send HTTP HEAD request"""
        return self.request("HEAD", url, **kw)

    def get(self, url: str, **kw) -> Response:
        """Send HTTP GET request"""
        return self.request("GET", url, **kw)

    def post(self, url: str, **kw) -> Response:
        """Send HTTP POST request"""
        return self.request("POST", url, **kw)

    def put(self, url: str, **kw) -> Response:
        """Send HTTP PUT request"""
        return self.request("PUT", url, **kw)

    def patch(self, url: str, **kw) -> Response:
        """Send HTTP PATCH request"""
        return self.request("PATCH", url, **kw)

    def delete(self, url: str, **kw) -> Response:
        """Send HTTP DELETE request"""
        return self.request("DELETE", url, **kw)


# Backwards compatible API:

_default_session = None  # pylint: disable=invalid-name


class _FakeSSLSocket:
    def __init__(self, socket: CircuitPythonSocketType, tls_mode: int) -> None:
        self._socket = socket
        self._mode = tls_mode
        self.settimeout = socket.settimeout
        self.send = socket.send
        self.recv = socket.recv
        self.close = socket.close

    def connect(self, address: Tuple[str, int]) -> None:
        """connect wrapper to add non-standard mode parameter"""
        try:
            return self._socket.connect(address, self._mode)
        except RuntimeError as error:
            raise OSError(errno.ENOMEM) from error


class _FakeSSLContext:
    def __init__(self, iface: InterfaceType) -> None:
        self._iface = iface

    def wrap_socket(
        self, socket: CircuitPythonSocketType, server_hostname: Optional[str] = None
    ) -> _FakeSSLSocket:
        """Return the same socket"""
        # pylint: disable=unused-argument
        return _FakeSSLSocket(socket, self._iface.TLS_MODE)


def set_socket(
    sock: SocketpoolModuleType, iface: Optional[InterfaceType] = None
) -> None:
    """Legacy API for setting the socket and network interface. Use a `Session` instead."""
    global _default_session  # pylint: disable=global-statement,invalid-name
    if not iface:
        # pylint: disable=protected-access
        _default_session = Session(sock, _FakeSSLContext(sock._the_interface))
    else:
        _default_session = Session(sock, _FakeSSLContext(iface))
    sock.set_interface(iface)


def request(
    method: str,
    url: str,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    stream: bool = False,
    timeout: float = 1,
) -> None:
    """Send HTTP request"""
    # pylint: disable=too-many-arguments
    _default_session.request(
        method,
        url,
        data=data,
        json=json,
        headers=headers,
        stream=stream,
        timeout=timeout,
    )


def head(url: str, **kw):
    """Send HTTP HEAD request"""
    return _default_session.request("HEAD", url, **kw)


def get(url: str, **kw):
    """Send HTTP GET request"""
    return _default_session.request("GET", url, **kw)


def post(url: str, **kw):
    """Send HTTP POST request"""
    return _default_session.request("POST", url, **kw)


def put(url: str, **kw):
    """Send HTTP PUT request"""
    return _default_session.request("PUT", url, **kw)


def patch(url: str, **kw):
    """Send HTTP PATCH request"""
    return _default_session.request("PATCH", url, **kw)


def delete(url: str, **kw):
    """Send HTTP DELETE request"""
    return _default_session.request("DELETE", url, **kw)
