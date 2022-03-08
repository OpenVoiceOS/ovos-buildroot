################################################################################
#
# python-ovos-tts-plugin-mimic
#
################################################################################

PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION = b33d75959557b800dd87b7e459269823ed664b8a
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SITE = $(call github,OpenVoiceOS,ovos-tts-plugin-mimic,$(PYTHON_OVOS_TTS_PLUGIN_MIMIC_VERSION))
PYTHON_OVOS_TTS_PLUGIN_MIMIC_SETUP_TYPE = setuptools

$(eval $(python-package))
