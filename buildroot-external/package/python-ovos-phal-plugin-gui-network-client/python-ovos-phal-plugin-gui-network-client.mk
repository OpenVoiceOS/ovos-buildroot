################################################################################
#
# python-ovos-phal-plugin-gui-network-client
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION = 847ab586387503b044e497f544a843f0d02110cb
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-gui-network-client,$(PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_GUI_NETWORK_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
