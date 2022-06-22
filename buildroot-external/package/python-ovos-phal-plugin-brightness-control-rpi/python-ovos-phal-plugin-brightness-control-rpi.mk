################################################################################
#
# python-ovos-phal-plugin-brightness-control-rpi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION = 9b28b0ed6ebbda78c3a8686f00c4da290fc08b4d
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-brightness-control-rpi,$(PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_LICENSE_FILES = LICENSE

$(eval $(python-package))
