################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = a3c5257f633d3a4689179ac7c98d19bc0f6d2e69
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_VOSK_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
