################################################################################
#
# python-ovos-phal-plugin-wifi-setup
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_VERSION = b8da31ce1b3767d1d88c8908e1f9f31a830b9262
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-wifi-setup,$(PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_LICENSE_FILES = LICENSE

$(eval $(python-package))
