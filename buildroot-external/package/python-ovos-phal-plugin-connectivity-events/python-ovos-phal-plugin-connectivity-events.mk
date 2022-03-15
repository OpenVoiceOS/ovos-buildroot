################################################################################
#
# python-ovos-phal-plugin-connectivity-events
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_VERSION = d8914f388efe0dcfd024eacc1501d7e391c17662
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-connectivity-events,$(PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
