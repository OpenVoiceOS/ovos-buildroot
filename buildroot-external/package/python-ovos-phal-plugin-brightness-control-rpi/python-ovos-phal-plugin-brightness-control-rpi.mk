################################################################################
#
# python-ovos-phal-plugin-brightness-control-rpi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION = ca22f4591864ed96c6eba92251a905d4a6e4e010
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-brightness-control-rpi,$(PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_LICENSE_FILES = LICENSE

$(eval $(python-package))
