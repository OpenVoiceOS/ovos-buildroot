################################################################################
#
# python-ovos-phal-plugin-brightness-control-rpi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION = ff32c12942929b4d7de56ef2ed23b6c7a320b782
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-brightness-control-rpi,$(PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_LICENSE_FILES = LICENSE

$(eval $(python-package))
