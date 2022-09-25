################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 0b350e65a92ecba4dcd5b944fb9e8ed916ad5f8d
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools

$(eval $(python-package))
