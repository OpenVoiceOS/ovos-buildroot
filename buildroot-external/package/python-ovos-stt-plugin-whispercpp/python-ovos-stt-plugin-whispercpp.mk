################################################################################
#
# python-ovos-stt-plugin-whispercpp
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_VERSION = 630db8ff8b2ea8f56c30f39254d880b0f572c921
PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-whispercpp,$(PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_VERSION))
PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_WHISPERCPP_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
