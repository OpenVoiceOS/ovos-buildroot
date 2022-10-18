################################################################################
#
# python-ovos-stt-server-plugin
#
################################################################################

PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION = 61a632319e4020304b4b1c1b7fbbf1d12a5c66a5
PYTHON_OVOS_STT_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-stt-server-plugin,$(PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_STT_SERVER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_SERVER_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
