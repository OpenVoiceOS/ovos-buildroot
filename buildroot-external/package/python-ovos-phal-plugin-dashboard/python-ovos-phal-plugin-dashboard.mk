################################################################################
#
# python-ovos-phal-plugin-dashboard
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION = 4ab48f75c577218acf11b6e5f4dbe54300b63567
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-dashboard,$(PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
