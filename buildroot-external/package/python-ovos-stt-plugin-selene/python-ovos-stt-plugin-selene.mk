################################################################################
#
# python-ovos-stt-plugin-selene
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION = bb4f4d45566265460420e5988a9d37fc41d1a7ce
PYTHON_OVOS_STT_PLUGIN_SELENE_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-selene,$(PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION))
PYTHON_OVOS_STT_PLUGIN_SELENE_SETUP_TYPE = setuptools

$(eval $(python-package))
