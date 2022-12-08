from ovos_plugin_manager.utils import load_plugin, find_plugins, PluginTypes, PluginConfigTypes
from ovos_plugin_manager.templates.phal import PHALPlugin, AdminPlugin


def find_phal_plugins():
    return find_plugins(PluginTypes.PHAL)


def get_phal_configs():
    return {plug: get_phal_module_configs(plug)
            for plug in find_phal_plugins()}


def get_phal_module_configs(module_name):
    # PHAL plugins return [list of config dicts] or {module_name: [list of config dicts]}
    cfgs = load_plugin(module_name + ".config",  PluginConfigTypes.PHAL)
    return {module_name: cfgs} if isinstance(cfgs, list) else cfgs


def find_admin_plugins():
    return find_plugins(PluginTypes.ADMIN)


def get_admin_configs():
    return {plug: get_admin_module_configs(plug)
            for plug in find_admin_plugins()}


def get_admin_module_configs(module_name):
    # admin plugins return [list of config dicts] or {module_name: [list of config dicts]}
    cfgs = load_plugin(module_name + ".config",  PluginConfigTypes.ADMIN)
    return {module_name: cfgs} if isinstance(cfgs, list) else cfgs
