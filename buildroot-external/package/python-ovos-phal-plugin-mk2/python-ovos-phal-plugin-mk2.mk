################################################################################
#
# python-ovos-phal-plugin-mk2
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_MK2_VERSION = 14e765a9a2bc2231171b1569da233a9a0714f3eb
PYTHON_OVOS_PHAL_PLUGIN_MK2_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-mk2,$(PYTHON_OVOS_PHAL_PLUGIN_MK2_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_MK2_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_MK2_LICENSE_FILES = LICENSE

$(eval $(python-package))
