import time
from functools import wraps
from threading import Timer, Lock
from uuid import uuid4

from ovos_config.config import Configuration
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message, FakeBus
from ovos_utils.network_utils import is_connected

from ovos_backend_client.api import DeviceApi, BackendType
from ovos_backend_client.exceptions import BackendDown, InternetDown, HTTPError
from ovos_backend_client.identity import IdentityManager
from ovos_backend_client.backends.selene import SELENE_API_URL


def is_backend_disabled():
    config = Configuration()
    if not config.get("server"):
        # missing server block implies disabling backend
        return True
    return config["server"].get("disabled") or False


def requires_backend(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_backend_disabled():
            return f(*args, **kwargs)
        return {}

    return decorated


def has_been_paired():
    """ Determine if this device has ever been paired with a backend

    Returns:
        bool: True if ever paired with backend (not factory reset)
    """
    # This forces a load from the identity file in case the pairing state
    # has recently changed
    ident = IdentityManager.load()
    # NOTE: even offline backend creates a dummy identity file
    return ident.uuid is not None and ident.uuid != ""


def is_paired(ignore_errors=True, url=None, version="v1", identity_file=None, backend_type=None):
    """Determine if this device is actively paired with a web backend

    Determines if the installation of Mycroft has been paired by the user
    with the backend system, and if that pairing is still active.

    Returns:
        bool: True if paired with backend
    """
    if is_backend_disabled():
        return True

    # check if pairing is valid
    api = DeviceApi(url=url, version=version, identity_file=identity_file, backend_type=backend_type)
    return api.identity.uuid and check_remote_pairing(ignore_errors, url=url, version=version,
                                                      identity_file=identity_file, backend_type=backend_type)


def check_remote_pairing(ignore_errors, url=None, version="v1", identity_file=None, backend_type=None):
    """Check that a basic backend endpoint accepts our pairing.

    Args:
        ignore_errors (bool): True if errors should be ignored when

    Returns:
        True if pairing checks out, otherwise False.
    """
    try:
        return bool(DeviceApi(url=url, version=version,
                              identity_file=identity_file, backend_type=backend_type).get())
    except HTTPError as e:
        if e.response.status_code == 401:
            return False
        error = e
    except Exception as e:
        error = e

    LOG.warning(f'Could not get device info: {error}')

    if ignore_errors:
        return False

    if isinstance(error, HTTPError):
        if is_connected():
            raise BackendDown from error
        else:
            raise InternetDown from error
    else:
        raise error


class PairingManager:
    poll_frequency = 5  # secs between checking server for activation

    def __init__(self, bus=None,
                 enclosure=None,
                 code_callback=None,
                 error_callback=None,
                 success_callback=None,
                 start_callback=None,
                 restart_callback=None,
                 end_callback=None,
                 pairing_url="home.mycroft.ai",
                 api_url=SELENE_API_URL,
                 version="v1",
                 identity_file=None,
                 backend_type=None):
        if enclosure:
            LOG.warning("enclosure argument has been deprecated, it is no longer used")
        self.pairing_url = pairing_url
        self.api_url = api_url
        self.restart_callback = restart_callback
        self.code_callback = code_callback
        self.error_callback = error_callback
        self.success_callback = success_callback
        self.start_callback = start_callback
        self.end_callback = end_callback

        self.bus = bus or FakeBus()
        self.api = DeviceApi(url=api_url, version=version,
                             identity_file=identity_file, backend_type=backend_type)
        self.data = None
        self.time_code_expires = None
        self.uuid = str(uuid4())
        self.activator = None
        self.activator_lock = Lock()
        self.activator_cancelled = False
        self.counter_lock = Lock()
        self.count = -1  # for repeating pairing code. -1 = not running
        self.num_failed_codes = 0

    def set_api_url(self, url,  version="v1", identity_file=None, backend_type=BackendType.SELENE):
        if not url.startswith("http"):
            url = f"http://{url}"
        self.api_url = url
        self.api = DeviceApi(url, version=version,
                             identity_file=identity_file,
                             backend_type=backend_type)

    def shutdown(self):
        with self.activator_lock:
            self.activator_cancelled = True
            if self.activator:
                self.activator.cancel()
        if self.activator:
            self.activator.join()

    def kickoff_pairing(self):
        self.data = None

        # Kick off pairing...
        with self.counter_lock:
            if self.count > -1:
                # We snuck in to this handler somehow while the pairing
                # process is still being setup.  Ignore it.
                LOG.debug("Ignoring call to kickoff_pairing")
                return
            # Not paired or already pairing, so start the process.
            self.count = 0

        LOG.debug("Kicking off pairing sequence")

        try:
            # Obtain a pairing code from the backend
            self.data = self.api.get_code(self.uuid)
            self.handle_pairing_code()

            # Keep track of when the code was obtained.  The codes expire
            # after 20 hours.
            self.time_code_expires = time.monotonic() + 72000  # 20 hours
        except Exception:
            time.sleep(10)
            # Call restart pairing here
            # Bail out after Five minutes (5 * 6 attempts at 10 seconds
            # interval)
            if self.num_failed_codes < 5 * 6:
                self.num_failed_codes += 1
                self.abort_and_restart(quiet=True)
            else:
                self.end_pairing('connection.error')
                self.num_failed_codes = 0
            return

        self.num_failed_codes = 0  # Reset counter on success

        if self.start_callback:
            self.start_callback()

        if not self.activator:
            self.__create_activator()

    def check_for_activate(self):
        """Method is called every 10 seconds by Timer. Checks if user has
        activated the device yet on home.mycroft.ai and if not repeats
        the pairing code every 60 seconds.
        """
        try:
            # Attempt to activate.  If the user has completed pairing on the,
            # backend, this will succeed.  Otherwise it throws and HTTPError()

            token = self.data.get("token")

            LOG.info(f"Attempting device activation @ {self.api_url}")
            login = self.api.activate(self.uuid, token)  # HTTPError() thrown
            if not login:
                raise ValueError("Received empty identity data!")
            LOG.info(f"Identity data received!: {login.get('uuid')}")

            # When we get here, the pairing code has been entered on the
            # backend and pairing can now be saved.
            # The following is kinda ugly, but it is really critical that we
            # get this saved successfully or we need to let the user know that
            # they have to perform pairing all over again at the website.
            try:
                IdentityManager.save(login)
            except Exception as e:
                LOG.debug("First save attempt failed: " + repr(e))
                time.sleep(2)
                try:
                    IdentityManager.save(login)
                except Exception as e2:
                    # Something must be seriously wrong
                    LOG.debug("Second save attempt failed: " + repr(e2))
                    self.abort_and_restart()
                    return

            # Assume speaking is the pairing code.  Stop TTS of that.
            self.bus.emit(Message("mycroft.audio.speech.stop"))

            self.bus.emit(Message("mycroft.paired", login))

            if self.success_callback:
                self.success_callback()

            # Un-mute.  Would have been muted during onboarding for a new
            # unit, and not dangerous to do if pairing was started
            # independently.
            self.bus.emit(Message("mycroft.mic.unmute", None))

        except HTTPError:
            # speak pairing code every 60th second
            with self.counter_lock:
                if self.count == 0:
                    self.handle_pairing_code()
                self.count = (self.count + 1) % 6

            if time.monotonic() > self.time_code_expires:
                # After 20 hours the token times out.  Restart
                # the pairing process.
                with self.counter_lock:
                    self.count = -1
                self.data = None
                if self.restart_callback:
                    self.restart_callback()
            else:
                # trigger another check in 10 seconds
                self.__create_activator()
        except Exception as e:
            LOG.debug("Unexpected error: " + repr(e))
            self.abort_and_restart()

    def end_pairing(self, error_dialog):
        """Resets the pairing and don't restart it.

        Arguments:
            error_dialog: Reason for the ending of the pairing process.
        """
        self.bus.emit(Message("mycroft.mic.unmute", None))
        self.data = None
        self.count = -1
        if self.end_callback:
            self.end_callback(error_dialog)

    def abort_and_restart(self, quiet=False):
        # restart pairing sequence
        LOG.debug("Aborting Pairing")
        # Reset state variables for a new pairing session
        with self.counter_lock:
            self.count = -1
        self.activator = None
        self.data = None  # Clear pairing code info
        LOG.info("Restarting pairing process")
        if self.error_callback:
            self.error_callback(quiet)
        self.bus.emit(Message("mycroft.not.paired",
                              data={'quiet': quiet}))

    def __create_activator(self):
        # Create a timer that will poll the backend in 10 seconds to see
        # if the user has completed the device registration process
        with self.activator_lock:
            if not self.activator_cancelled:
                self.activator = Timer(self.poll_frequency,
                                       self.check_for_activate)
                self.activator.daemon = True
                self.activator.start()

    def handle_pairing_code(self):
        """Log pairing code."""
        code = self.data.get("code")
        LOG.info("Pairing code: " + code)
        # emit info message, allows PHAL plugins to perform actions
        # eg. the mk1 faceplate scrolls the code
        self.bus.emit(Message("mycroft.pairing.code", self.data))
        if self.code_callback:
            self.code_callback(code)
