################################################################################
#
# python-ovos-stt-plugin-server
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_SERVER_VERSION = 8f440da949ced2f823383b87acb7c7e502cdb7ff
PYTHON_OVOS_STT_PLUGIN_SERVER_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-server,$(PYTHON_OVOS_STT_PLUGIN_SERVER_VERSION))
PYTHON_OVOS_STT_PLUGIN_SERVER_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_SERVER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
