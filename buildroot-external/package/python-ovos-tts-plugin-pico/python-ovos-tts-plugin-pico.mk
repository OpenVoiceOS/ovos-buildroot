################################################################################
#
# python-ovos-tts-plugin-pico
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION = 6acd4c3863befbb9f9f9fca576ec9222166429cd
PYTHON_OVOS_TTS_PLUGIN_PICO_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-pico,$(PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION))
PYTHON_OVOS_TTS_PLUGIN_PICO_SETUP_TYPE = setuptools

$(eval $(python-package))
