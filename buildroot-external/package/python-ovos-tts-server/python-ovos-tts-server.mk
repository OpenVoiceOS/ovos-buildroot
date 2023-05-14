################################################################################
#
# python-ovos-tts-server
#
################################################################################

PYTHON_OVOS_TTS_SERVER_VERSION = 86369a266bac906bc4c82de267e0ec6c089c1772
PYTHON_OVOS_TTS_SERVER_SITE = $(call github,OpenVoiceOS,ovos-tts-server,$(PYTHON_OVOS_TTS_SERVER_VERSION))
PYTHON_OVOS_TTS_SERVER_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_SERVER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
