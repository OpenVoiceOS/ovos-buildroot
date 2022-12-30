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

import socket

try:
    import netifaces
    import requests
    from requests.exceptions import MissingSchema, InvalidSchema, InvalidURL, \
        ConnectionError
except ImportError:
    raise ImportError("netifaces or requests not available,"
                      " pip install neon-utils[network]")


def get_ip_address() -> str:
    """
    Returns the IPv4 address of the default interface (This is a public IP for server implementations)
    :return: IP Address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_adapter_info(interface: str = "default") -> dict:
    """
    Returns MAC and IP info for the specified gateway
    :param interface: Name of network interface to check
    :return: Dict of mac, IPv4 and IPv6 addresses
    """
    gateways = netifaces.gateways()
    if interface not in gateways:
        raise IndexError("Requested Interface Not Found")
    if netifaces.AF_INET not in gateways[interface]:
        raise IndexError("Requested Interface not connected!")
    device = gateways[interface][netifaces.AF_INET][1]
    mac = netifaces.ifaddresses(device)[netifaces.AF_LINK][0]['addr']
    ip4 = netifaces.ifaddresses(device)[netifaces.AF_INET][0]['addr']
    ip6 = netifaces.ifaddresses(device)[netifaces.AF_INET6][0]['addr']
    return {"ipv4": ip4, "ipv6": ip6, "mac": mac}


def check_url_response(url: str = "https://google.com") -> bool:
    """
    Checks if the passed url is accessible.
    :param url: URL to connect to (http/https schema expected)
    :returns: resp.ok if request is completed, False if ConnectionError is raised
    """
    if not isinstance(url, str):
        raise ValueError(f"{url} is not a str")
    try:
        resp = requests.get(url)
        return resp.ok
    except MissingSchema:
        return check_url_response(f"http://{url}")
    except InvalidSchema:
        raise ValueError(f"{url} is not a valid http url")
    except InvalidURL:
        raise ValueError(f"{url} is not a valid URL")
    except ConnectionError:
        # Offline Response
        return False
    except Exception as e:
        raise e


def check_online(valid_urls: tuple = ("https://google.com", "https://github.com")) -> bool:
    """
    Checks if device is online by pinging expected online remote URLs
    :param valid_urls: list of URL's to use
    :returns: True if remote sites can be reached, else False
    """
    if not isinstance(valid_urls, tuple):
        raise ValueError(f"Expected tuple, got {type(valid_urls)}")
    for url in valid_urls:
        try:
            if check_url_response(url):
                return True
        except ValueError:
            pass

    return False


def check_port_is_open(addr: str, port: int) -> bool:
    """
    Checks if the specified port at addr is open
    :param addr: IP or URL to query
    :param port: port to check
    :returns: True if the port is reachable, else False
    """
    test_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_connection.settimeout(5)
    status = test_connection.connect_ex((addr, port))
    return status == 0

