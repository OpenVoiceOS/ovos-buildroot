################################################################################
#
# python-ovos-ww-plugin-precise
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_PRECISE_VERSION = e3e70c6dbf036c47a72f20dcd69ce30ddc495fbb
PYTHON_OVOS_WW_PLUGIN_PRECISE_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-precise,$(PYTHON_OVOS_WW_PLUGIN_PRECISE_VERSION))
PYTHON_OVOS_WW_PLUGIN_PRECISE_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_PRECISE_LICENSE_FILES = LICENSE

$(eval $(python-package))
