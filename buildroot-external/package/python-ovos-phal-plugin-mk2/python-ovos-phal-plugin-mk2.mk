################################################################################
#
# python-ovos-phal-plugin-mk2
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_MK2_VERSION = ca6ea0a21274e623c1d1934b5d201e0dd579ee71
PYTHON_OVOS_PHAL_PLUGIN_MK2_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-mk2,$(PYTHON_OVOS_PHAL_PLUGIN_MK2_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_MK2_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_MK2_LICENSE_FILES = LICENSE

$(eval $(python-package))
