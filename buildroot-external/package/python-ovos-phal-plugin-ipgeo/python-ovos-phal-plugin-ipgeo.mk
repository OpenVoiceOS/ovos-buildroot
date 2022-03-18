################################################################################
#
# python-ovos-phal-plugin-ipgeo
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_IPGEO_VERSION = 8fdbdfdf572ddb99c46f09344ffc6eb373502a35
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-ipgeo,$(PYTHON_OVOS_PHAL_PLUGIN_IPGEO_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_LICENSE_FILES = LICENSE

$(eval $(python-package))
