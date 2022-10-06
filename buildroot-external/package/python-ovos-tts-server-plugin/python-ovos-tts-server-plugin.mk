################################################################################
#
# python-ovos-tts-server-plugin
#
################################################################################

PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION = 692d129030a3876b7e77f92a3a3a6285a4a5537a
PYTHON_OVOS_TTS_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-tts-server-plugin,$(PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_TTS_SERVER_PLUGIN_SETUP_TYPE = setuptools

$(eval $(python-package))
