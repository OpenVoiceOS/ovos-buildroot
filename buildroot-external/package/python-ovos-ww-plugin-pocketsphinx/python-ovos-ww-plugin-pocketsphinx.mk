################################################################################
#
# python-ovos-ww-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION = 06183f4cf51e94cf0fd76cdb3f134789d787330a
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-pocketsphinx,$(PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
