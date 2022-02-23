################################################################################
#
# python-ovos-stt-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION = 19972630dbf95f3a77d15f5c184a5c524c57f7c9
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-pocketsphinx,$(PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools

$(eval $(python-package))
