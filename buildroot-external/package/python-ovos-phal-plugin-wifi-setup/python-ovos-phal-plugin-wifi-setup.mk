################################################################################
#
# python-ovos-phal-plugin-wifi-setup
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_VERSION = 00072c88de3406fae4a14c38e64f9708494850d6
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-wifi-setup,$(PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_WIFI_SETUP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
