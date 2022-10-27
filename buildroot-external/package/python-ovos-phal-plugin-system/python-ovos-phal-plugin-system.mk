################################################################################
#
# python-ovos-phal-plugin-system
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION = 5f480dc788eca3989dc6111f4c7bf7a52418fd04
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-system,$(PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_LICENSE_FILES = LICENSE

$(eval $(python-package))
