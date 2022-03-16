################################################################################
#
# python-ovos-phal-plugin-balena-wifi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION = a1570c84487b5e742719b26aafb0ee20f1f1d588
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-balena-wifi,$(PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_LICENSE_FILES = LICENSE

$(eval $(python-package))
