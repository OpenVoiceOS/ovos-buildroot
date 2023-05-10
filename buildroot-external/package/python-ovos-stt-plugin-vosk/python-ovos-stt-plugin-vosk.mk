################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 3bde4c117bf76ceb5645eff8cf534157f0e4e00d
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_VOSK_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
