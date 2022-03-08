################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION = 34f07aa3a355cd988baa58c0a86ec445f8f8ec3a
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise-lite,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LITE_LICENSE_FILES = LICENSE

$(eval $(python-package))
