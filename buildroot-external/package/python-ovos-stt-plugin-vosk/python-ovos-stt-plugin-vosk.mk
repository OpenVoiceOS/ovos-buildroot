################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 29abe652d1989e4caea87a29685a1c2409f1347a
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_VOSK_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
