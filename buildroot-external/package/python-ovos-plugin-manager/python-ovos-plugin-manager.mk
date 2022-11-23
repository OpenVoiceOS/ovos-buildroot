################################################################################
#
# python-ovos-plugin-manager
#
################################################################################

PYTHON_OVOS_PLUGIN_MANAGER_VERSION = a6795b6a1d4f14c7730abe56d696b1a496c6aaba
PYTHON_OVOS_PLUGIN_MANAGER_SITE = $(call github,OpenVoiceOS,OVOS-plugin-manager,$(PYTHON_OVOS_PLUGIN_MANAGER_VERSION))
PYTHON_OVOS_PLUGIN_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PLUGIN_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PLUGIN_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
