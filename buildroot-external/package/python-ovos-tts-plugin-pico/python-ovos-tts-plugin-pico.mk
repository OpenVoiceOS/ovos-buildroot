################################################################################
#
# python-ovos-tts-plugin-pico
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION = 3f1ce8e42041b65c161b44627f4b16f79ef2eea4
PYTHON_OVOS_TTS_PLUGIN_PICO_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-pico,$(PYTHON_OVOS_TTS_PLUGIN_PICO_VERSION))
PYTHON_OVOS_TTS_PLUGIN_PICO_SETUP_TYPE = setuptools

$(eval $(python-package))
