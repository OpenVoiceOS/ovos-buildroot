################################################################################
#
# python-ovos-stt-server-plugin
#
################################################################################

PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION = eb6d149d3c095bb1b52424e7830451d11a99357f
PYTHON_OVOS_STT_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-stt-server-plugin,$(PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_STT_SERVER_PLUGIN_SETUP_TYPE = setuptools

$(eval $(python-package))
