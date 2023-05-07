################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION = 485f1c39cbb9542c9b0885207f33df91313ed565
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise-lite,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_LICENSE_FILES = LICENSE

$(eval $(python-package))
