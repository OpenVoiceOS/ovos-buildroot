################################################################################
#
# python-ovos-stt-plugin-chromium
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION = b9cb384156f02010bd50eb2ce897179651206185
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-chromium,$(PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION))
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SETUP_TYPE = setuptools

$(eval $(python-package))
