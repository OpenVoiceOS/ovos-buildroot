################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION = 71f78a7f74ece22fb8f673abc6c1be9ab3593831
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise-lite,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_LICENSE_FILES = LICENSE

$(eval $(python-package))
