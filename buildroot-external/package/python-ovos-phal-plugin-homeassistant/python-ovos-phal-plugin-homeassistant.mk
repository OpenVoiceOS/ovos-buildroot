################################################################################
#
# python-ovos-phal-plugin-homeassistant
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_VERSION = 5f07ec0053685c197e3da7dca617682a7e1e7ea5
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-homeassistant,$(PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_HOMEASSISTANT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
