################################################################################
#
# python-ovos-stt-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION = bce847812c67e57e821fa259f428a2787c4e43cb
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-pocketsphinx,$(PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools

$(eval $(python-package))
