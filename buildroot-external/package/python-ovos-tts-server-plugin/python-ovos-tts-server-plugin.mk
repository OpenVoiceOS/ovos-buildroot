################################################################################
#
# python-ovos-tts-server-plugin
#
################################################################################

PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION = ef34c87997311298e8c7a055d4a7585b9204be2c
PYTHON_OVOS_TTS_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-tts-server-plugin,$(PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_TTS_SERVER_PLUGIN_SETUP_TYPE = setuptools

$(eval $(python-package))
