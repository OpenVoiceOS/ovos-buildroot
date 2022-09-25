################################################################################
#
# python-ovos-vad-plugin-webrtcvad
#
################################################################################

PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_VERSION = bf9636f2e06493b90d9b19dfccbe0376a41c68b1
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_SITE = $(call github,OpenVoiceOS,ovos-vad-plugin-webrtcvad,$(PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_VERSION))
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_SETUP_TYPE = setuptools
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_LICENSE_FILES = LICENSE

$(eval $(python-package))
