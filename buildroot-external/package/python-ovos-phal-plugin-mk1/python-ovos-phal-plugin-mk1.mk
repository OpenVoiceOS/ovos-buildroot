################################################################################
#
# python-ovos-phal-plugin-mk1
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_MK1_VERSION = 01066aa33678469445fe65bbb9efae75b0d8693e
PYTHON_OVOS_PHAL_PLUGIN_MK1_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-mk1,$(PYTHON_OVOS_PHAL_PLUGIN_MK1_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_MK1_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_MK1_LICENSE_FILES = LICENSE

$(eval $(python-package))
