from ovos_plugin_manager.phal import find_phal_plugins
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
from ovos_utils.process_utils import ProcessStatus, StatusCallbackMap
from ovos_workshop import OVOSAbstractApplication


def on_ready():
    LOG.info('PHAL is ready.')


def on_stopping():
    LOG.info('PHAL is shutting down...')


def on_error(e='Unknown'):
    LOG.error(f'PHAL failed to launch ({e}).')


def on_alive():
    LOG.info('PHAL is alive')


def on_started():
    LOG.info('PHAL is started')


class PHAL(OVOSAbstractApplication):
    """
    Args:
        config (dict): PHAL config, usually from mycroft.conf
        bus (MessageBusClient): mycroft messagebus connection
        watchdog: (callable) function to call periodically indicating
                  operational status.
    """

    def __init__(self, config=None, bus=None,
                 on_ready=on_ready, on_error=on_error,
                 on_stopping=on_stopping, on_started=on_started, on_alive=on_alive,
                 watchdog=lambda: None, name="PHAL", **kwargs):
        super().__init__(skill_id=f"ovos.{name}")
        ready_hook = kwargs.get('ready_hook', on_ready)
        error_hook = kwargs.get('error_hook', on_error)
        stopping_hook = kwargs.get('stopping_hook', on_stopping)
        alive_hook = kwargs.get('alive_hook', on_alive)
        started_hook = kwargs.get('started_hook', on_started)
        callbacks = StatusCallbackMap(on_ready=ready_hook,
                                      on_error=error_hook,
                                      on_stopping=stopping_hook,
                                      on_alive=alive_hook,
                                      on_started=started_hook)
        self.status = ProcessStatus(name, callback_map=callbacks)
        self._watchdog = watchdog  # TODO implement
        if not config:
            try:
                config = read_mycroft_config()["PHAL"]
            except:
                config = {}
        self.config = config
        self.bus = bus or get_mycroft_bus()
        self.drivers = {}
        self.status.bind(self.bus)

    def load_plugins(self):
        for name, plug in find_phal_plugins().items():
            config = self.config.get(name) or {}
            if hasattr(plug, "validator"):
                enabled = plug.validator.validate(config)
            else:
                enabled = config.get("enabled")
            if enabled:
                try:
                    self.drivers[name] = plug(bus=self.bus, config=config)
                    LOG.info(f"PHAL plugin loaded: {name}")
                except Exception:
                    LOG.exception(f"failed to load PHAL plugin: {name}")
                    continue

    def start(self):
        self.status.set_started()
        try:
            self.load_plugins()
            self.status.set_ready()
        except Exception as e:
            self.status.set_error(e)

    def shutdown(self):
        self.status.set_stopping()
