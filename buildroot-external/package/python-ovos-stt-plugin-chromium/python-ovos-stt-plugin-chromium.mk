################################################################################
#
# python-ovos-stt-plugin-chromium
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION = f2ae0d54b962ddb3ee33f8178c367f1d4d8e6118
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-chromium,$(PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION))
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
