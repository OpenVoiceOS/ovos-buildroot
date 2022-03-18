################################################################################
#
# python-ovos-phal-plugin-balena-wifi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION = f523bb4582bb01c90a7cec273feb49e578551057
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-balena-wifi,$(PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BALENA_WIFI_LICENSE_FILES = LICENSE

$(eval $(python-package))
