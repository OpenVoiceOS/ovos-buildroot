################################################################################
#
# python-ovos-stt-plugin-selene
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION = 31bdc3a89cbfa23f668ae53ff2459af43905ddad
PYTHON_OVOS_STT_PLUGIN_SELENE_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-selene,$(PYTHON_OVOS_STT_PLUGIN_SELENE_VERSION))
PYTHON_OVOS_STT_PLUGIN_SELENE_SETUP_TYPE = setuptools

$(eval $(python-package))
