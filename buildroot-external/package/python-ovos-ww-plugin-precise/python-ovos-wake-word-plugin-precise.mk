################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_VERSION = 766bc2d1e0a71f9b0e3f6a4f2fe1fbc981f90ae2
PYTHON_OVOS_WW_PLUGIN_PRECISE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LICENSE_FILES = LICENSE

$(eval $(python-package))
