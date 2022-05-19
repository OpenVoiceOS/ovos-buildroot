################################################################################
#
# python-ovos-vad-plugin-webrtcvad
#
################################################################################

PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_VERSION = 441bddb041938287f8f62a2f45a9d2f4addf6d2c
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_SITE = $(call github,OpenVoiceOS,ovos-vad-plugin-webrtcvad,$(PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_VERSION))
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_SETUP_TYPE = setuptools
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_LICENSE_FILES = LICENSE

$(eval $(python-package))
