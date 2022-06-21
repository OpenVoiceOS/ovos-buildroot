################################################################################
#
# python-ovos-phal-plugin-brightness-control-rpi
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION = 696c048c43cc8ef99b5e1c3e2435d8570f4b247a
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-brightness-control-rpi,$(PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_BRIGHTNESS_CONTROL_RPI_LICENSE_FILES = LICENSE

$(eval $(python-package))
