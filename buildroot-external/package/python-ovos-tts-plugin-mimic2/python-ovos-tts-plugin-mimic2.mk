################################################################################
#
# python-ovos-tts-plugin-mimic2
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION = f81143e85d089928892a96185c01e9172df8aa16
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic2,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
