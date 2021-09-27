################################################################################
#
# python-ovos-tts-plugin-pico
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION = 568c80df9ad647ffb371e3ec7ca49e4f8aa0c6ec
PYTHON_OVOS_TTS_PLUGIN_PICO_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-pico,$(PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION))
PYTHON_OVOS_TTS_PLUGIN_PICO_SETUP_TYPE = setuptools

$(eval $(python-package))
