################################################################################
#
# python-ovos-tts-plugin-marytts
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MARYTTS_VERSION = 7401b9b23b3a8424af89f09979db6e8e893e2059
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-marytts,$(PYTHON_OVOS_TTS_PLUGIN_MARYTTS_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_SETUP_TYPE = setuptools

$(eval $(python-package))
