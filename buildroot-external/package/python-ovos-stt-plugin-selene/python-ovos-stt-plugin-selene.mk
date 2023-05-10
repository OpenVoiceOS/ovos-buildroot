################################################################################
#
# python-ovos-stt-plugin-selene
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION = 549f8583e706c44234257fcc39fa0f454c1e37b3
PYTHON_OVOS_STT_PLUGIN_SELENE_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-selene,$(PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION))
PYTHON_OVOS_STT_PLUGIN_SELENE_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_SELENE_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
