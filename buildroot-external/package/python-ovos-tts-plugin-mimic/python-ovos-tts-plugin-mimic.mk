################################################################################
#
# python-ovos-tts-plugin-mimic
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION = dd4a3d0d9d45beed1f7387c918a0bbba0ab41904
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_MIMIC_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
