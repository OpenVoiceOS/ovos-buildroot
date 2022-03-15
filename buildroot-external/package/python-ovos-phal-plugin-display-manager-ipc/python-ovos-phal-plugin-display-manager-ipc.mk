################################################################################
#
# python-ovos-phal-plugin-display-manager-ipc
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_VERSION = f22f9d41b3927b5cf71e8de0f040dee94e6e6ca6
PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-display-manager-ipc,$(PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DISPLAY_MANAGER_IPC_LICENSE_FILES = LICENSE

$(eval $(python-package))
