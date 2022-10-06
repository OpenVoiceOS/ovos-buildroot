################################################################################
#
# python-ovos-phal-plugin-gui-network-client
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION = 6d96c47cc853bce6ec160a3aff2be3e0f8ae8748
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-gui-network-client,$(PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
