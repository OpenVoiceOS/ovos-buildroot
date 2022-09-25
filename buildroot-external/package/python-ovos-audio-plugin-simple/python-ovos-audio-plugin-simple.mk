################################################################################
#
# python-ovos-audio-plugin-simple
#
################################################################################

PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION = e53e165de9c334e0541ce5b205dcdd86efc5dc0a
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SITE = $(call github,OpenVoiceOS,ovos-audio-plugin-simple,$(PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION))
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_LICENSE = Apache-2.0

$(eval $(python-package))
