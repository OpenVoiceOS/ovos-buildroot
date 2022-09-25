################################################################################
#
# python-ovos-phal-plugin-brightness-control-rpi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION = 4ad633cd6ad7386514d4bd688858adaa82fe54d3
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-brightness-control-rpi,$(PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_LICENSE_FILES = LICENSE

$(eval $(python-package))
