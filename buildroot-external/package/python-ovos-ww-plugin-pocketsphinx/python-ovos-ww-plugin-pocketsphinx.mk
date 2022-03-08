################################################################################
#
# python-ovos-ww-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION = be6154b02b6cf9768f1aead14c338d753e76a656
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-pocketsphinx,$(PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
