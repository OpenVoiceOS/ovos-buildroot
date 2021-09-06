################################################################################
#
# python-ovos-ww-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION = 86d22179f5bd85bd55c9ffec1a2f071129d9947c
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-pocketsphinx,$(PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
