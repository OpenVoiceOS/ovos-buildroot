################################################################################
#
# python-ovos-phal-plugin-network-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION = 44882b77da1e478adbcdb43b5eef75f070a132ea
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-network-manager,$(PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NETWORK_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
