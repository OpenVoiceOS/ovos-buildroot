import socket
import requests


def get_ip():
    # taken from https://stackoverflow.com/a/28950776/13703283
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_external_ip():
    return requests.get('https://api.ipify.org').text


def is_connected_dns(host="1.1.1.1"):
    try:
        # connect to the host -- tells us if the host is actually reachable
        socket.create_connection((host, 53))
        return True
    except OSError:
        pass
    return False


def is_connected_http(host="http://duckduckgo.com"):
    try:
        status = requests.head(host).status_code
        return True
    except OSError:
        pass
    return False


def is_connected():
    return any((is_connected_dns(), is_connected_http()))
