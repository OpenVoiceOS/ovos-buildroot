################################################################################
#
# python-ovos-tts-server
#
################################################################################

PYTHON_OVOS_TTS_SERVER_VERSION = b9ee84c48ab6ab5655fffa032359752ab10d2c9d
PYTHON_OVOS_TTS_SERVER_SITE = $(call github,OpenVoiceOS,ovos-tts-server,$(PYTHON_OVOS_TTS_SERVER_VERSION))
PYTHON_OVOS_TTS_SERVER_SETUP_TYPE = setuptools

$(eval $(python-package))
