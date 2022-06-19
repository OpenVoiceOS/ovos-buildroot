################################################################################
#
# python-ovos-audio-plugin-simple
#
################################################################################

PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION = 02f485bf2f73858b277f8842e93ddbc1c521458b
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SITE = $(call github,OpenVoiceOS,ovos-audio-plugin-simple,$(PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION))
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_LICENSE = Apache-2.0

$(eval $(python-package))
