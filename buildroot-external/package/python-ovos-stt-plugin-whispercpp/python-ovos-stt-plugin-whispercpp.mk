################################################################################
#
# python-ovos-stt-plugin-whispercpp
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_VERSION = 2eac10f51d6cc80c5d75894babbdc4f902d6273f
PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-whispercpp,$(PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_VERSION))
PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
