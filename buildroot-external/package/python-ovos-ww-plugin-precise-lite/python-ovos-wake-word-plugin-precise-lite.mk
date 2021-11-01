################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION = e2379c7a82ef865fb3502b709bb632a7ae2aa56c
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise-lite,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_LICENSE_FILES = LICENSE

$(eval $(python-package))
