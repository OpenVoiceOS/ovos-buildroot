################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = b86c3636ed862150e0980f0698b978384c240b80
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools

$(eval $(python-package))
