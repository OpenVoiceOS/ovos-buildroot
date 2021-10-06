################################################################################
#
# python-ovos-ocp-audio-plugin
#
################################################################################

PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION = 16f1bb53a0f7fcd97aab27e6367e80111876958d
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-audio-plugin,$(PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION))
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_AUDIO_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
