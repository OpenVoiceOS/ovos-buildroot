################################################################################
#
# python-ovos-phal-plugin-wifi-setup
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_VERSION = 45c74d0a6a1c78ef5f5a67c5ae7145339a21eb4f
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-wifi-setup,$(PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_LICENSE_FILES = LICENSE

$(eval $(python-package))
