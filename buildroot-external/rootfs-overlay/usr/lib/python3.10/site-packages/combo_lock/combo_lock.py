# Copyright 2018 Mycroft AI Inc.
#
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
from base64 import b64encode
from threading import Lock
from os.path import exists, join
from os import chmod
from combo_lock.util import get_ram_directory
from filelock import FileLock, Timeout


class ComboLock:
    """ A combined process and thread lock.

    Arguments:
        path (str): path to the lockfile for the lock
    """
    def __init__(self, path):
        # Create lock file if it doesn't exist and set permissions for
        # all users to lock/unlock
        if not exists(path):
            f = open(path, 'w+')
            f.close()
            chmod(path, 0o777)
        self.plock = FileLock(path)
        self.tlock = Lock()

    def acquire(self, blocking=True):
        """ Acquire lock, locks thread and process lock.

        Arguments:
            blocking(bool): Set's blocking mode of acquire operation.
                            Default True.

        Returns: True if lock succeeded otherwise False
        """
        if not blocking:
            # Lock thread
            tlocked = self.tlock.acquire(blocking=False)
            if not tlocked:
                return False
            # Lock process
            try:
                self.plock.acquire(timeout=0.01)
                plocked = True
            except Timeout:
                plocked = False
            if not plocked:
                # Release thread lock if process couldn't be locked
                self.tlock.release()
                return False
        else:  # blocking, just wait and acquire ALL THE LOCKS!!!
            self.tlock.acquire()
            self.plock.acquire()
        return True

    def release(self):
        """ Release acquired lock. """
        self.plock.release()
        self.tlock.release()

    def __enter__(self):
        """ Context handler, acquires lock in blocking mode. """
        self.acquire()
        return self

    def __exit__(self, _type, value, traceback):
        """ Releases the lock. """
        self.release()


def _filename_from_name(name):
    """Create a filesystem safe filename from name.

    Arguments:
        name (string): name to encode

    Returns:
        (string) encoded version of the name.
    """
    encoded_name = b64encode(name.encode(), altchars=b'-_')
    return encoded_name.decode() + ".lock"


class NamedLock(ComboLock):
    def __init__(self, name):
        filename = _filename_from_name(name)
        path = join(get_ram_directory("combo_locks"), filename)
        super().__init__(path)
        self.name = name
