################################################################################
#
# python-ovos-phal-plugin-network-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION = 1ab1407599182db0d96ad93dc7f40bc0cdb383c8
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-network-manager,$(PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
