from ovos_plugin_manager.phal import find_admin_plugins
from ovos_utils import wait_for_exit_signal
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.log import LOG

from ovos_PHAL import PHAL


def on_admin_ready():
    LOG.info('PHAL Admin is ready.')


def on_admin_stopping():
    LOG.info('PHAL Admin is shutting down...')


def on_admin_error(e='Unknown'):
    LOG.error(f'PHAL Admin failed to launch ({e}).')


def on_admin_alive():
    LOG.info('PHAL Admin is alive')


def on_admin_started():
    LOG.info('PHAL Admin is started')


class AdminPHAL(PHAL):
    """
    Args:
        config (dict): PHAL admin config, usually from mycroft.conf PHAL.admin section
        bus (MessageBusClient): mycroft messagebus connection
        watchdog: (callable) function to call periodically indicating
                  operational status.
    """

    def __init__(self, config=None, bus=None, on_ready=on_admin_ready, on_error=on_admin_error,
                 on_stopping=on_admin_stopping, on_started=on_admin_started, on_alive=on_admin_alive,
                 watchdog=lambda: None, name="PHAL.admin", **kwargs):
        if not config:
            try:
                config = read_mycroft_config()
                config = config.get("PHAL", {}).get("admin", {})
            except:
                config = {}
        super().__init__(config, bus, on_ready, on_error, on_stopping, on_started, on_alive, watchdog, name, **kwargs)

    def load_plugins(self):
        for name, plug in find_admin_plugins().items():
            config = self.config.get(name) or {}
            enabled = config.get("enabled")
            if not enabled:
                continue  # require explicit enabling by user
            if hasattr(plug, "validator"):
                enabled = plug.validator.validate(config)

            if enabled:
                try:
                    self.drivers[name] = plug(bus=self.bus, config=config)
                    LOG.info(f"PHAL Admin plugin loaded: {name}")
                except Exception:
                    LOG.exception(f"failed to load PHAL Admin plugin: {name}")
                    continue


def main(ready_hook=on_admin_ready, error_hook=on_admin_error, stopping_hook=on_admin_stopping):
    # config read from mycroft.conf
    # "PHAL": {
    #   "admin": {
    #     "ovos-PHAL-plugin-system": {"enabled": True}
    #   }
    # }
    phal = AdminPHAL(on_error=error_hook, on_ready=ready_hook, on_stopping=stopping_hook)
    phal.start()
    wait_for_exit_signal()
    phal.shutdown()


if __name__ == "__main__":
    main()
