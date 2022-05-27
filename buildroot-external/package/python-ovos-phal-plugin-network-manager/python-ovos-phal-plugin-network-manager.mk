################################################################################
#
# python-ovos-phal-plugin-network-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION = a039ac7f17f32f5b283cfcbec80b3163ec22a95a
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-network-manager,$(PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
