################################################################################
#
# python-ovos-tts-plugin-pico
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION = eb2a588d1f7a94b988adad72b80ba4aa2101dd68
PYTHON_OVOS_TTS_PLUGIN_PICO_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-pico,$(PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION))
PYTHON_OVOS_TTS_PLUGIN_PICO_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_PICO_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
