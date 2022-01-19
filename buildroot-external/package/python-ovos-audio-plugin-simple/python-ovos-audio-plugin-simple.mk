################################################################################
#
# python-ovos-audio-plugin-simple
#
################################################################################

PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION = 0.0.1a1
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SOURCE = ovos_audio_plugin_simple-$(PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_VERSION).tar.gz
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SITE = https://files.pythonhosted.org/packages/f6/19/58acf46fb4a3bb52a6eee12fc3e90461251c5ce0a7bfa1c0d568c618a607
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_SETUP_TYPE = setuptools
PYTHON_OVOS_AUDIO_PLUGIN_SIMPLE_LICENSE = Apache-2.0

$(eval $(python-package))
