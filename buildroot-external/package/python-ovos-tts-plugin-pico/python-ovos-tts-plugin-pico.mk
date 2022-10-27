################################################################################
#
# python-ovos-tts-plugin-pico
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION = 2b1c96256751c6a1d6db4e88e471de02b38bcf62
PYTHON_OVOS_TTS_PLUGIN_PICO_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-pico,$(PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION))
PYTHON_OVOS_TTS_PLUGIN_PICO_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_PICO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
