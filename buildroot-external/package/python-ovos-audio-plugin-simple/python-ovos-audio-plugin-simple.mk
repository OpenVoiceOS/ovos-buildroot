################################################################################
#
# python-ovos-audio-plugin-simple
#
################################################################################

PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION = 6dddaad629e5afbe8161d2c857c0e9dd50783b63
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SITE = $(call github,OpenVoiceOS,ovos-audio-plugin-simple,$(PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION))
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_LICENSE = Apache-2.0

$(eval $(python-package))
