################################################################################
#
# python-ovos-ocp-audio-plugin
#
################################################################################

PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION = b45a68c193a4948054d40118d886e7878ecb5d96
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-audio-plugin,$(PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION))
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_AUDIO_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
