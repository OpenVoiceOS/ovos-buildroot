################################################################################
#
# python-ovos-vad-plugin-webrtcvad
#
################################################################################

PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_VERSION = e08ad05426f3742f74f17f182ced7255c3a580f9
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_SITE = $(call github,OpenVoiceOS,ovos-vad-plugin-webrtcvad,$(PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_VERSION))
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_SETUP_TYPE = setuptools
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_LICENSE_FILES = LICENSE
PYTHON_OVOS_VAD_PLUGIN_WEBRTCVAD_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
