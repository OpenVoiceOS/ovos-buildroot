################################################################################
#
# python-ovos-phal-plugin-display-manager-ipc
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_VERSION = 65599cc2efa842af71ae3db25a5f491f52810178
PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-display-manager-ipc,$(PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_LICENSE_FILES = LICENSE

$(eval $(python-package))
