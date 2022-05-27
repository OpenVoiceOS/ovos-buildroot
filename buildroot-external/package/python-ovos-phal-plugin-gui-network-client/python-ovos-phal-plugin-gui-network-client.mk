################################################################################
#
# python-ovos-phal-plugin-gui-network-client
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION = c35ca8e510f3f0576db637222b15c34fe9997ba3
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-gui-network-client,$(PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
