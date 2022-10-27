################################################################################
#
# python-ovos-stt-server-plugin
#
################################################################################

PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION = c8d7dea5a6875221f152828629846979f52e6d05
PYTHON_OVOS_STT_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-stt-server-plugin,$(PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_STT_SERVER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_SERVER_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
