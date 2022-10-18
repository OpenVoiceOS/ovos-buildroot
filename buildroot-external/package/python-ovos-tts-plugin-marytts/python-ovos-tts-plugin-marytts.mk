################################################################################
#
# python-ovos-tts-plugin-marytts
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MARYTTS_VERSION = 207961106063ddc29f66b6b8f9077f85e7806480
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-marytts,$(PYTHON_OVOS_TTS_PLUGIN_MARYTTS_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
