################################################################################
#
# python-ovos-tts-server-plugin
#
################################################################################

PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION = 17e8664cfad5c236bb1f6dd2a07c0604fe41d4a0
PYTHON_OVOS_TTS_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-tts-server-plugin,$(PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_TTS_SERVER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_SERVER_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
