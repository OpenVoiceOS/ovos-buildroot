################################################################################
#
# python-ovos-phal-plugin-gui-network-client
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION = b5ac0eb6f5cdfeb5490f6394d9538e5493fb4f98
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-gui-network-client,$(PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
