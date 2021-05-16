################################################################################
#
# python-ovos-plugin-manager
#
################################################################################

PYTHON_OVOS_PLUGIN_MANAGER_VERSION = f3ddcb7ad63cc15716796f7165f88ece153fb338
PYTHON_OVOS_PLUGIN_MANAGER_SITE = $(call github,OpenVoiceOS,OVOS-plugin-manager,$(PYTHON_OVOS_PLUGIN_MANAGER_VERSION))
PYTHON_OVOS_PLUGIN_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PLUGIN_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
