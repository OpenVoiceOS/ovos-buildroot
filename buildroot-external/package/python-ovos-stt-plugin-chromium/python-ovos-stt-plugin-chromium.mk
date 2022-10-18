################################################################################
#
# python-ovos-stt-plugin-chromium
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION = 41dfccd1e583ce11fdd454c106518c5317c9c858
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-chromium,$(PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION))
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
