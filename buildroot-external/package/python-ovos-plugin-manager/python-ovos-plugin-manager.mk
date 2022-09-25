################################################################################
#
# python-ovos-plugin-manager
#
################################################################################

PYTHON_OVOS_PLUGIN_MANAGER_VERSION = 2d988e2fd8b302bde1aa1c384ba720cbf93a40d7
PYTHON_OVOS_PLUGIN_MANAGER_SITE = $(call github,OpenVoiceOS,OVOS-plugin-manager,$(PYTHON_OVOS_PLUGIN_MANAGER_VERSION))
PYTHON_OVOS_PLUGIN_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PLUGIN_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
