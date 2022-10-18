################################################################################
#
# python-ovos-phal-plugin-dashboard
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION = dc24be3b94078c3e9f437cdf5e4991070d6dc2a2
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-dashboard,$(PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
