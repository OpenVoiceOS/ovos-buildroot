################################################################################
#
# python-ovos-phal-plugin-respeaker-4mic
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_4MIC_VERSION = 0f54c45b1d7e1d461053dfd617522ee4e59a80ba
PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_4MIC_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-respeaker-4mic,$(PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_4MIC_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_4MIC_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_4MIC_LICENSE_FILES = LICENSE

$(eval $(python-package))
