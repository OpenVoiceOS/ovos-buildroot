################################################################################
#
# python-ovos-phal-plugin-homeassistant
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_VERSION = df606469ed56965a3274ff5d7b62ec20c4b22f75
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-homeassistant,$(PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
