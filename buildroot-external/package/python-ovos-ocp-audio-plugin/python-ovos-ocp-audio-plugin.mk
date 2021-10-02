################################################################################
#
# python-ovos-ocp-audio-plugin
#
################################################################################

PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION = 9c17e4c565c82548abf4650459423254fce85089
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-audio-plugin,$(PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION))
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_AUDIO_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
