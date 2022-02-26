################################################################################
#
# python-ovos-ww-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION = 2344c4761f8a4b50dc522533791a9527cfd9b148
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-pocketsphinx,$(PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
