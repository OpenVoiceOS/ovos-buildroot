################################################################################
#
# python-ovos-ww-plugin-vosk
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_VOSK_VERSION = 1ee4917e19d8f39f9944c11f3f596a5e0cf2ff58
PYTHON_OVOS_WW_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-vosk,$(PYTHON_OVOS_WW_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_WW_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_VOSK_LICENSE_FILES = LICENSE

$(eval $(python-package))
