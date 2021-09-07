################################################################################
#
# python-ovos-tts-plugin-mimic
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION = 6088ebfd7c78220a0531997482e46bebc50357ff
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SETUP_TYPE = setuptools

$(eval $(python-package))
