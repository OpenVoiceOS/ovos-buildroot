################################################################################
#
# python-ovos-tts-plugin-mimic
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION = a6ce5e7e620c081532fa34dab1c5ae39a5c90f17
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SETUP_TYPE = setuptools

$(eval $(python-package))
