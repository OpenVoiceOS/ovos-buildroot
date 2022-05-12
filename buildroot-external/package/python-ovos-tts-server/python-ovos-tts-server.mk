################################################################################
#
# python-ovos-tts-server
#
################################################################################

PYTHON_OVOS_TTS_SERVER_VERSION = ceef8aacce4bf58b949573083c7686220f150c5e
PYTHON_OVOS_TTS_SERVER_SITE = $(call github,OpenVoiceOS,ovos-tts-server,$(PYTHON_OVOS_TTS_SERVER_VERSION))
PYTHON_OVOS_TTS_SERVER_SETUP_TYPE = setuptools

$(eval $(python-package))
