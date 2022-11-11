################################################################################
#
# python-ovos-phal-plugin-system
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION = 4e697036a6ace2105247954b64a003e602358747
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-system,$(PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_LICENSE_FILES = LICENSE

$(eval $(python-package))
