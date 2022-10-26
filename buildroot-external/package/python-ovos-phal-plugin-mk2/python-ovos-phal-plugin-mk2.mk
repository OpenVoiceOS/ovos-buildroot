################################################################################
#
# python-ovos-phal-plugin-mk2
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_MK2_VERSION = e71e4bff6480b81b604d29c15f078c2187174d93
PYTHON_OVOS_PHAL_PLUGIN_MK2_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-mk2,$(PYTHON_OVOS_PHAL_PLUGIN_MK2_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_MK2_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_MK2_LICENSE_FILES = LICENSE

$(eval $(python-package))
