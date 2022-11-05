################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 808527c7187584177a656bb16988c8fd5ab0bdcb
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_VOSK_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
