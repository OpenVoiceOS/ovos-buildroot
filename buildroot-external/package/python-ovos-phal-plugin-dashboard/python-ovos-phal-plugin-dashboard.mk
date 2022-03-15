################################################################################
#
# python-ovos-phal-plugin-dashboard
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION = 08bf17333d6d4fc67e62311d0be1bfd43f21f436
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-dashboard,$(PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_LICENSE_FILES = LICENSE

$(eval $(python-package))
