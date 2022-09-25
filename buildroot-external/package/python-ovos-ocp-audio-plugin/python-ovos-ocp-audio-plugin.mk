################################################################################
#
# python-ovos-ocp-audio-plugin
#
################################################################################

PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION = 43659772c92448449fe1e1a7ae27e8194c067b87
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-audio-plugin,$(PYTHON_OVOS_OCP_AUDIO_PLUGIN_VERSION))
PYTHON_OVOS_OCP_AUDIO_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_AUDIO_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
