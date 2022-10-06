################################################################################
#
# python-ovos-phal-plugin-system
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION = fa499c355a38ff6533c7e71e40b4344f2f673969
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-system,$(PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_SYSTEM_LICENSE_FILES = LICENSE

$(eval $(python-package))
