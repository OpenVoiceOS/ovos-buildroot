################################################################################
#
# python-ovos-phal-plugin-network-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION = c04d1d84faa30fd5c897581b05249546fe1d6025
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-network-manager,$(PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
