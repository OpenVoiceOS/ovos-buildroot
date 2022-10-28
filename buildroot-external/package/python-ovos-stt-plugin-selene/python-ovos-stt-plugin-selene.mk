################################################################################
#
# python-ovos-stt-plugin-selene
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION = 49e5f16da293c83c54d4d71e9d836f44fe469634
PYTHON_OVOS_STT_PLUGIN_SELENE_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-selene,$(PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION))
PYTHON_OVOS_STT_PLUGIN_SELENE_SETUP_TYPE = setuptools

$(eval $(python-package))
