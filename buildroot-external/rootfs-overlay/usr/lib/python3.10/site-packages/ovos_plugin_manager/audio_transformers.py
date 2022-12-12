from ovos_plugin_manager.utils import load_plugin, find_plugins, PluginTypes, PluginConfigTypes


def find_audio_transformer_plugins():
    return find_plugins(PluginTypes.AUDIO_TRANSFORMER)


def get_audio_transformer_configs():
    return {plug: get_audio_transformer_module_configs(plug)
            for plug in find_audio_transformer_plugins()}


def get_audio_transformer_module_configs(module_name):
    return load_plugin(module_name + ".config", PluginConfigTypes.AUDIO_TRANSFORMER)


def load_audio_transformer_plugin(module_name):
    """Wrapper function for loading audio_transformer plugin.

    Arguments:
        (str) Mycroft audio_transformer module name from config
    Returns:
        class: found audio_transformer plugin class
    """
    return load_plugin(module_name, PluginTypes.AUDIO_TRANSFORMER)

