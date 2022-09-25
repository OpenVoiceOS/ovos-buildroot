################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION = a39d467ae106892edfbb547d0012706dc3127002
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise-lite,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_LICENSE_FILES = LICENSE

$(eval $(python-package))
