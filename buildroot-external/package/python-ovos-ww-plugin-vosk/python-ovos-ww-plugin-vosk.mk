################################################################################
#
# python-ovos-ww-plugin-vosk
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_VOSK_VERSION = b5fbf1a553f97c27df9a0cfe54465aeed7b6105c
PYTHON_OVOS_WW_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-vosk,$(PYTHON_OVOS_WW_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_WW_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_VOSK_LICENSE_FILES = LICENSE

$(eval $(python-package))
