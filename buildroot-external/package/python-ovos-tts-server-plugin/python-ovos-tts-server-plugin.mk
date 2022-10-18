################################################################################
#
# python-ovos-tts-server-plugin
#
################################################################################

PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION = 43f44f64a1ced28f93dd6a633fcea2e4d00e5c2e
PYTHON_OVOS_TTS_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-tts-server-plugin,$(PYTHON_OVOS_TTS_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_TTS_SERVER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_SERVER_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
