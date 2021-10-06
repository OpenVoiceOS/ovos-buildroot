################################################################################
#
# python-ovos-ocp-audio-plugin
#
################################################################################

PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION = 60860148e33d30523bde404c9b6b627f15e07931
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-audio-plugin,$(PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION))
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_AUDIO_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
