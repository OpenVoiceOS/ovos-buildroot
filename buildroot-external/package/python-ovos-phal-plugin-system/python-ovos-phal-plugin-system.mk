################################################################################
#
# python-ovos-phal-plugin-system
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION = fe0e683edd1ca082aad2113bda535c44dc2a352e
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-system,$(PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_LICENSE_FILES = LICENSE

$(eval $(python-package))
