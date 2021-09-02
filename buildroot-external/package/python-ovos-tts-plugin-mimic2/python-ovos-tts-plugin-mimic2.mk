################################################################################
#
# python-ovos-tts-plugin-mimic2
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION = 9c389383dd1cafa2811363b9fbc22d89b823b3c9
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic2,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SETUP_TYPE = setuptools

$(eval $(python-package))
