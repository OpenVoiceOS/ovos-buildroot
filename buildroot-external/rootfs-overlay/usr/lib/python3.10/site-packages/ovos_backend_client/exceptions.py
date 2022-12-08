from requests import RequestException
from requests import HTTPError


class BackendDown(RequestException):
    pass


class InternetDown(RequestException):
    pass
