################################################################################
#
# python-ovos-tts-plugin-mimic2
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION = b0e3ce483ad4154a79e55277817f8f85083ef1fb
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic2,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SETUP_TYPE = setuptools

$(eval $(python-package))
