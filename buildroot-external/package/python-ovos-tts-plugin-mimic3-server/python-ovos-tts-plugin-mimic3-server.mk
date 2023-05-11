################################################################################
#
# python-ovos-tts-plugin-mimic3-server
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_VERSION = 9a31cc1505d7c1520ff6d885b3b443077611f478
PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic3-server,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
