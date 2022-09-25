################################################################################
#
# python-ovos-phal-plugin-dashboard
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION = d1fefaaca98697082aba472d0eeaaf528188beec
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-dashboard,$(PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_LICENSE_FILES = LICENSE

$(eval $(python-package))
