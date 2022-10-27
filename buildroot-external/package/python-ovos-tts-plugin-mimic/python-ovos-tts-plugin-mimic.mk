################################################################################
#
# python-ovos-tts-plugin-mimic
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION = efff5ea111d594cac8bafd257c0d03c5c9e7ac1f
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SETUP_TYPE = setuptools
PYTHON_OVOS_TTS_PLUGIN_MIMIC_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
