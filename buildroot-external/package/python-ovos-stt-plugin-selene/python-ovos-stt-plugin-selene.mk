################################################################################
#
# python-ovos-stt-plugin-selene
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION = d96863f34fec89747932a7e4e2c36ce88534976f
PYTHON_OVOS_STT_PLUGIN_SELENE_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-selene,$(PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION))
PYTHON_OVOS_STT_PLUGIN_SELENE_SETUP_TYPE = setuptools

$(eval $(python-package))
