################################################################################
#
# python-ovos-tts-plugin-marytts
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MARYTTS_VERSION = 16180516e21bc447991ef3d1697f8427573edb35
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-marytts,$(PYTHON_OVOS_TTS_PLUGIN_MARYTTS_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MARYTTS_SETUP_TYPE = setuptools

$(eval $(python-package))
