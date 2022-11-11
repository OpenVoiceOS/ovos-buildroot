################################################################################
#
# python-ovos-tts-plugin-mimic3-server
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_VERSION = efabecb074e2e53811b9e801dec0844485b7474f
PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic3-server,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC3_SERVER_SETUP_TYPE = setuptools

$(eval $(python-package))
