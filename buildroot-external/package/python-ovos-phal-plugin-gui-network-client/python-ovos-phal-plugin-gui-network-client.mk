################################################################################
#
# python-ovos-phal-plugin-gui-network-client
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION = d11130c5b72c482a0a3412070681ed225272c11f
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-gui-network-client,$(PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
