################################################################################
#
# python-ovos-phal-plugin-gpsd
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_GPSD_VERSION = a5859a89dddd5fd2c889a1464fbcab29943f2df0
PYTHON_OVOS_PHAL_PLUGIN_GPSD_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-gpsd,$(PYTHON_OVOS_PHAL_PLUGIN_GPSD_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_GPSD_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_GPSD_LICENSE_FILES = LICENSE

$(eval $(python-package))
