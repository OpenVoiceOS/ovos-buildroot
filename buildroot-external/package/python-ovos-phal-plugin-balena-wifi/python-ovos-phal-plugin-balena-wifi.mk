################################################################################
#
# python-ovos-phal-plugin-balena-wifi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION = 06baad7f2321f8e27d1dbdee0b5ffc1f1e76557b
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-balena-wifi,$(PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_LICENSE_FILES = LICENSE

$(eval $(python-package))
