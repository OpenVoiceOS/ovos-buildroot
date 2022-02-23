################################################################################
#
# python-ovos-audio-plugin-simple
#
################################################################################

PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION = 48849519be7487351513384da3cd5a29215122fd
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SITE = $(call github,OpenVoiceOS,ovos-audio-plugin-simple,$(PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION))
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_LICENSE = Apache-2.0

$(eval $(python-package))
