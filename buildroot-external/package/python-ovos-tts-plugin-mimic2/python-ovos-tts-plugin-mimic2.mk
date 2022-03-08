################################################################################
#
# python-ovos-tts-plugin-mimic2
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION = 38afc96213fd2dfe91291ac9a1813f0b774057d8
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic2,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SETUP_TYPE = setuptools

$(eval $(python-package))
