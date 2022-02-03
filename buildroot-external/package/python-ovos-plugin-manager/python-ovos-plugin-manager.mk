################################################################################
#
# python-ovos-plugin-manager
#
################################################################################

PYTHON_OVOS_PLUGIN_MANAGER_VERSION = ad188a206ef5ef43adab9be65a5d92fdd8728d43
PYTHON_OVOS_PLUGIN_MANAGER_SITE = $(call github,OpenVoiceOS,OVOS-plugin-manager,$(PYTHON_OVOS_PLUGIN_MANAGER_VERSION))
PYTHON_OVOS_PLUGIN_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PLUGIN_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
