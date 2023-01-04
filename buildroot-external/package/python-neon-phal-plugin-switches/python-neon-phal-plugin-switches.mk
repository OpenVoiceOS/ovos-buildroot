################################################################################
#
# python-neon-phal-plugin-switches
#
################################################################################

PYTHON_NEON_PHAL_PLUGIN_SWITCHES_VERSION = e5f7fd5d1e8f2effadbe76e13b03e7d03006ab32
PYTHON_NEON_PHAL_PLUGIN_SWITCHES_SITE = $(call github,NeonGeckoCom,neon-phal-plugin-switches,$(PYTHON_NEON_PHAL_PLUGIN_SWITCHES_VERSION))
PYTHON_NEON_PHAL_PLUGIN_SWITCHES_SETUP_TYPE = setuptools
PYTHON_NEON_PHAL_PLUGIN_SWITCHES_LICENSE_FILES = LICENSE

$(eval $(python-package))
