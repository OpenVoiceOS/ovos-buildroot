from ovos_plugin_manager.utils import PluginConfigTypes, load_plugin, find_plugins, PluginTypes
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
from ovos_config import Configuration


def setup_audio_service(service_module, config=None, bus=None):
    """Run the appropriate setup function and return created service objects.

    Arguments:
        service_module: Python module to run
        config (dict): Mycroft configuration dict
        bus (MessageBusClient): Messagebus interface
    Returns:
        (list) List of created services.
    """
    config = config or Configuration()
    bus = bus or get_mycroft_bus()
    if (hasattr(service_module, 'autodetect') and
            callable(service_module.autodetect)):
        try:
            return service_module.autodetect(config, bus)
        except Exception as e:
            LOG.error('Failed to autodetect audio service. ' + repr(e))
    elif hasattr(service_module, 'load_service'):
        try:
            return service_module.load_service(config, bus)
        except Exception as e:
            LOG.error('Failed to load audio service. ' + repr(e))
    else:
        return None


def find_audio_service_plugins():
    return find_plugins(PluginTypes.AUDIO)


def get_audio_service_configs():
    return {plug: get_audio_service_module_configs(plug)
            for plug in find_audio_service_plugins()}


def get_audio_service_module_configs(module_name):
    return load_plugin(module_name + ".config", PluginConfigTypes.AUDIO)


def load_audio_service_plugins(config=None, bus=None):
    """Load installed audioservice plugins.

    Arguments:
        config: Mycroft core configuration
        bus: Mycroft messagebus

    Returns:
        List of started services
    """
    bus = bus or get_mycroft_bus()
    plugin_services = []
    found_plugins = find_audio_service_plugins()
    for plugin_name, plugin_module in found_plugins.items():
        LOG.info(f'Loading audio service plugin: {plugin_name}')
        service = setup_audio_service(plugin_module, config, bus)
        if service:
            plugin_services += service
    return plugin_services
