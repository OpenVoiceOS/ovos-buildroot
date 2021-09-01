################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 188843cabcc994c1a351f3cedf87298a7368d0bc
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools

$(eval $(python-package))
