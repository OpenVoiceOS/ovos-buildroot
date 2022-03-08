################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_VERSION = 4f6d460a146a02e33795d401c6de1a83701d762f
PYTHON_OVOS_WW_PLUGIN_PRECISE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LICENSE_FILES = LICENSE

$(eval $(python-package))
