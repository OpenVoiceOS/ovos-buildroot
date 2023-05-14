################################################################################
#
# python-ovos-ww-plugin-vosk
#
################################################################################

PYTHON_OVOS_WW_PLUGIN_VOSK_VERSION = b106d28230443e31ce4d7dc4d3e579a69d3720cc
PYTHON_OVOS_WW_PLUGIN_VOSK_SITE = $(call github,OpenVoiceOS,ovos-ww-plugin-vosk,$(PYTHON_OVOS_WW_PLUGIN_VOSK_VERSION))
PYTHON_OVOS_WW_PLUGIN_VOSK_SETUP_TYPE = setuptools
PYTHON_OVOS_WW_PLUGIN_VOSK_LICENSE_FILES = LICENSE
PYTHON_OVOS_WW_PLUGIN_VOSK_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
