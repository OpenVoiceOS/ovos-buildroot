################################################################################
#
# python-ovos-tts-plugin-mimic
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION = ef12cf909a1123a31cdd1c0bfef3151a34b74f86
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SETUP_TYPE = setuptools

$(eval $(python-package))
