################################################################################
#
# python-ovos-phal-plugin-dashboard
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION = 1e0a3abb2f0c4dc9f0295c6426bb8017a7b4ecba
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-dashboard,$(PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_DASHBOARD_LICENSE_FILES = LICENSE

$(eval $(python-package))
