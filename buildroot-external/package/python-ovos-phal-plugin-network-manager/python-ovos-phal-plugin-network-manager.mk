################################################################################
#
# python-ovos-phal-plugin-network-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION = 0d5cd6ccbfb17230ccb0ea6e76e17733873bf58c
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-network-manager,$(PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
