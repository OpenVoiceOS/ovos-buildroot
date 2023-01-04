################################################################################
#
# python-neon-phal-plugin-linear-led
#
################################################################################

PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_VERSION = ee43c88355ad800fb0095490b19464f8adb55158
PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_SITE = $(call github,NeonGeckoCom,neon-phal-plugin-linear_led,$(PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_VERSION))
PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_SETUP_TYPE = setuptools
PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_LICENSE_FILES = LICENSE

$(eval $(python-package))
