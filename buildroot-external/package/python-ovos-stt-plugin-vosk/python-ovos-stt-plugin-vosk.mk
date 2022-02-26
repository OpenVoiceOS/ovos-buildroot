################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 73013824389fc900b2c3d9c130e86c4a0c1f7672
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-vosk,$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools

$(eval $(python-package))
