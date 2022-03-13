################################################################################
#
# python-ovos-tts-plugin-mimic2
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION = 730ef629a78461d7552bbe2b254c8b5081c703da
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic2,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC2_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC2_SETUP_TYPE = setuptools

$(eval $(python-package))
