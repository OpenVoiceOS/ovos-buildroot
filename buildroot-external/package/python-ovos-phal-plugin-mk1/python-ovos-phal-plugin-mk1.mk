################################################################################
#
# python-ovos-phal-plugin-mk1
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_MK1_VERSION = e8aa4f20f2a10792ad5c1cfa47719ab46a0117c4
PYTHON_OVOS_PHAL_PLUGIN_MK1_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-mk1,$(PYTHON_OVOS_PHAL_PLUGIN_MK1_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_MK1_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_MK1_LICENSE_FILES = LICENSE

$(eval $(python-package))
