################################################################################
#
# python-ovos-stt-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION = 3eb29b6a348927d85cc64de6dacf5a4c5116445c
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-pocketsphinx,$(PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools

$(eval $(python-package))
