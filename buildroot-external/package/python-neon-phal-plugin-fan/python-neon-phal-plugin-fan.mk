################################################################################
#
# python-neon-phal-plugin-fan
#
################################################################################

PYTHON_NEON_PHAL_PLUGIN_FAN_VERSION = 47b7030a0ec302146542179d13b12a61a3d95b4d
PYTHON_NEON_PHAL_PLUGIN_FAN_SITE = $(call github,NeonGeckoCom,neon-phal-plugin-fan,$(PYTHON_NEON_PHAL_PLUGIN_FAN_VERSION))
PYTHON_NEON_PHAL_PLUGIN_FAN_SETUP_TYPE = setuptools
PYTHON_NEON_PHAL_PLUGIN_FAN_LICENSE_FILES = LICENSE

$(eval $(python-package))
