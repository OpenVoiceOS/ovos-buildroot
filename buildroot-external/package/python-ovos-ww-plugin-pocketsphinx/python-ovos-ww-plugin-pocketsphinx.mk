################################################################################
#
# python-ovos-ww-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION = e19ffda95c4114743a82f97595d56b5ea2e35674
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-pocketsphinx,$(PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
