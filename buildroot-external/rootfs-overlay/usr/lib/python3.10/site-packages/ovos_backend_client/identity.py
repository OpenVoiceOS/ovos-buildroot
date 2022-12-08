import json
import os
import shutil
import time
from os.path import isfile, dirname, expanduser

from combo_lock import ComboLock
from ovos_utils.configuration import get_xdg_config_save_path, get_xdg_base
from ovos_utils.log import LOG

identity_lock = ComboLock('/tmp/identity-lock')


def find_identity():
    locations = [
        IdentityManager.OLD_IDENTITY_FILE,  # old location
        IdentityManager.IDENTITY_FILE,  # xdg location
        "~/mycroft-config/identity/identity2.json",  # smartgic docker default loc
    ]
    for loc in locations:
        loc = expanduser(loc)
        if isfile(loc):
            return loc
    return None


def load_identity():
    locations = [
        IdentityManager.OLD_IDENTITY_FILE,  # old location
        IdentityManager.IDENTITY_FILE,  # xdg location
        "~/mycroft-config/identity/identity2.json",  # smartgic docker default loc
    ]
    for loc in locations:
        loc = expanduser(loc)
        if isfile(loc):
            LOG.debug(f"identity found: {loc}")
            try:
                with open(loc) as f:
                    return json.load(f)
            except:
                LOG.error("invalid identity file!")
                continue
    return {}


class DeviceIdentity:
    def __init__(self, **kwargs):
        self.uuid = kwargs.get("uuid", "")
        self.access = kwargs.get("access", "")
        self.refresh = kwargs.get("refresh", "")
        self.expires_at = kwargs.get("expires_at", -1)

    def is_expired(self):
        return self.refresh and 0 < self.expires_at <= time.time()

    def has_refresh(self):
        return self.refresh != ""


class IdentityManager:
    IDENTITY_FILE = f"{get_xdg_config_save_path()}/identity/identity2.json"
    OLD_IDENTITY_FILE = expanduser(f"~/.{get_xdg_base()}/identity/identity2.json")
    __identity = None

    @classmethod
    def set_identity_file(cls, identity_path):
        cls.IDENTITY_FILE = identity_path
        cls.load()

    @staticmethod
    def _load():
        if isfile(IdentityManager.OLD_IDENTITY_FILE) and \
                not isfile(IdentityManager.IDENTITY_FILE):
            os.makedirs(dirname(IdentityManager.IDENTITY_FILE), exist_ok=True)
            shutil.move(IdentityManager.OLD_IDENTITY_FILE, IdentityManager.IDENTITY_FILE)
        if isfile(IdentityManager.IDENTITY_FILE):
            LOG.debug(f'Loading identity: {IdentityManager.IDENTITY_FILE}')
            try:
                with open(IdentityManager.IDENTITY_FILE) as f:
                    IdentityManager.__identity = DeviceIdentity(**json.load(f))
                return
            except Exception:
                pass
        IdentityManager.__identity = DeviceIdentity()

    @staticmethod
    def load(lock=True):
        try:
            if lock:
                identity_lock.acquire()
                IdentityManager._load()
        finally:
            if lock:
                identity_lock.release()
        return IdentityManager.__identity

    @staticmethod
    def save(login=None, lock=True):
        LOG.debug('Saving identity')
        if lock:
            identity_lock.acquire()
        try:
            if login:
                IdentityManager._update(login)

            os.makedirs(dirname(IdentityManager.IDENTITY_FILE), exist_ok=True)

            with open(IdentityManager.IDENTITY_FILE, "w") as f:
                json.dump(IdentityManager.__identity.__dict__, f)
                f.flush()
                os.fsync(f.fileno())
        finally:
            if lock:
                identity_lock.release()

    @staticmethod
    def _update(login=None):
        LOG.debug('Updating identity')
        login = login or {}
        expiration = login.get("expiration", -1)
        IdentityManager.__identity.uuid = login.get("uuid", "")
        IdentityManager.__identity.access = login.get("accessToken", "")
        IdentityManager.__identity.refresh = login.get("refreshToken", "")
        if expiration > 0:
            IdentityManager.__identity.expires_at = time.time() + expiration
        else:
            IdentityManager.__identity.expires_at = -1

    @staticmethod
    def update(login=None, lock=True):
        if lock:
            identity_lock.acquire()
        try:
            IdentityManager._update(login)
        finally:
            if lock:
                identity_lock.release()

    @staticmethod
    def get():
        if not IdentityManager.__identity:
            IdentityManager.load()
        return IdentityManager.__identity
