################################################################################
#
# python-neon-phal-plugin-linear-led
#
################################################################################

PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_VERSION = f7b23ccb5c91847ce2d3d50f6c7a213e21b64c80
PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_SITE = $(call github,NeonGeckoCom,neon-phal-plugin-linear_led,$(PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_VERSION))
PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_SETUP_TYPE = setuptools
PYTHON_NEON_PHAL_PLUGIN_LINEAR_LED_LICENSE_FILES = LICENSE

$(eval $(python-package))
