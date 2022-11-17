################################################################################
#
# python-ovos-phal-plugin-balena-wifi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION = 2cc99a00846d4e244f84b9c2d48305776b6169d9
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-balena-wifi,$(PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_LICENSE_FILES = LICENSE

$(eval $(python-package))
