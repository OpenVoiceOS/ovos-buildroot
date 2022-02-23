################################################################################
#
# python-ovos-phal-plugin-ipc2bus
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_IPC2BUS_VERSION = 3687d4ea8c8edca974f67119066e8a6316861b34
PYTHON_OVOS_PHAL_PLUGIN_IPC2BUS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-ipc2bus,$(PYTHON_OVOS_PHAL_PLUGIN_IPC2BUS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_IPC2BUS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_IPC2BUS_LICENSE_FILES = LICENSE

$(eval $(python-package))
