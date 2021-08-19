################################################################################
#
# python-ovos-stt-plugin-chromium
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION = 07c09f1892e50a7204647a5a4a0445697c877a70
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-chromium,$(PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION))
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SETUP_TYPE = setuptools

$(eval $(python-package))
