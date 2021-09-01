################################################################################
#
# python-ovos-stt-plugin-chromium
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION = 05806c4e4a13f33ef2e7fcad52f9679a2b777963
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-chromium,$(PYTHON_OVOS_STT_PLUGIN_CHROMIUM_VERSION))
PYTHON_OVOS_STT_PLUGIN_CHROMIUM_SETUP_TYPE = setuptools

$(eval $(python-package))
