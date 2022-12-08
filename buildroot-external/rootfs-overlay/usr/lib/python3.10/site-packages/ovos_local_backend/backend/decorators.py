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
from functools import wraps
from flask import make_response, request, Response
from ovos_local_backend.configuration import CONFIGURATION
from ovos_local_backend.database.settings import DeviceDatabase
from ovos_local_backend.utils.selene import attempt_selene_pairing, requires_selene_pairing
from ovos_backend_client.pairing import is_paired


def check_auth(uid, token):
    """This function is called to check if a access token is valid."""
    device = DeviceDatabase().get_device(uid)
    if device and device.token == token:
        return True
    return False


def requires_opt_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '').replace("Bearer ", "")
        uuid = kwargs.get("uuid") or auth.split(":")[-1]  # this split is only valid here, not selene
        device = DeviceDatabase().get_device(uuid)
        if device and device.opt_in:
            return f(*args, **kwargs)

    return decorated


def check_selene_pairing(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if CONFIGURATION.get("selene", {}).get("proxy_pairing"):
            attempt_selene_pairing()
        requires_selene = requires_selene_pairing(f.__name__)
        # check pairing with selene
        if requires_selene and not is_paired():
            return Response(
                'Could not verify your access level for that URL.\n'
                'You have to pair ovos backend with selene first', 401,
                {'WWW-Authenticate': 'Basic realm="BACKEND NOT PAIRED WITH SELENE"'})

        return f(*args, **kwargs)

    return decorated


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # skip_auth option is usually unsafe
        # use cases such as docker or ovos-qubes can not share a identity file between devices
        if not CONFIGURATION.get("skip_auth"):
            auth = request.headers.get('Authorization', '').replace("Bearer ", "")
            uuid = kwargs.get("uuid") or auth.split(":")[-1]  # this split is only valid here, not selene
            if not auth or not uuid or not check_auth(uuid, auth):
                return Response(
                    'Could not verify your access level for that URL.\n'
                    'You have to authenticate with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="NOT PAIRED"'})
        return f(*args, **kwargs)

    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        admin_key = CONFIGURATION.get("admin_key")
        auth = request.headers.get('Authorization', '').replace("Bearer ", "")
        if not auth or not admin_key or auth != admin_key:
            return Response(
                'Could not verify your access level for that URL.\n'
                'You have to authenticate with proper credentials', 401,
                {'WWW-Authenticate': 'Basic realm="NOT ADMIN"'})
        return f(*args, **kwargs)

    return decorated


def add_response_headers(headers=None):
    """This decorator adds the headers passed in to the response"""
    headers = headers or {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp

        return decorated_function

    return decorator


def noindex(f):
    """This decorator passes X-Robots-Tag: noindex"""
    return add_response_headers({'X-Robots-Tag': 'noindex'})(f)
