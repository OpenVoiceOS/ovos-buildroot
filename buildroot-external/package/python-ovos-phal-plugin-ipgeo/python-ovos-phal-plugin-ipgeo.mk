################################################################################
#
# python-ovos-phal-plugin-ipgeo
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_IPGEO_VERSION = 731dd02dda4e89134fab5f11352a77150cc74476
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-ipgeo,$(PYTHON_OVOS_PHAL_PLUGIN_IPGEO_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_IPGEO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
