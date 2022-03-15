################################################################################
#
# python-ovos-phal-plugin-system
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION = 13fe81eba8a23edd67121af3858c546e179fd95a
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-system,$(PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_LICENSE_FILES = LICENSE

$(eval $(python-package))
