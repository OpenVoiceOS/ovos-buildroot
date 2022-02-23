################################################################################
#
# python-ovos-phal-plugin-connectivity-events
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_VERSION = 3dce47382f2d25e0b8157bfa451a4fb18e0087d9
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-connectivity-events,$(PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONNECTIVITY_EVENTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
