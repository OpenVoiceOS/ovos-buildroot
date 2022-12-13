################################################################################
#
# python-ovos-plugin-manager
#
################################################################################

PYTHON_OVOS_PLUGIN_MANAGER_VERSION = d628bcae09a415188e432885647d8b6fc3072b43
PYTHON_OVOS_PLUGIN_MANAGER_SITE = $(call github,OpenVoiceOS,OVOS-plugin-manager,$(PYTHON_OVOS_PLUGIN_MANAGER_VERSION))
PYTHON_OVOS_PLUGIN_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PLUGIN_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PLUGIN_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
