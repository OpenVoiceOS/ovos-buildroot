################################################################################
#
# python-neon-tts-plugin-larynx_server
#
################################################################################

PYTHON_NEON_TTS_PLUGIN_LARYNX_SERVER_VERSION = e5c264bac0b46a8adcbcabe47b9b040fff07562f
PYTHON_NEON_TTS_PLUGIN_LARYNX_SERVER_SITE = $(call github,NeonGeckoCom,neon-tts-plugin-larynx_server,$(PYTHON_NEON_TTS_PLUGIN_LARYNX_SERVER_VERSION))
PYTHON_NEON_TTS_PLUGIN_LARYNX_SERVER_SETUP_TYPE = setuptools

$(eval $(python-package))
