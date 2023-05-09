################################################################################
#
# python-ovos-phal-plugin-connectivity-events
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_VERSION = 286bf5d2a8bb326edcca4353353a92f540c5b93b
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-connectivity-events,$(PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
