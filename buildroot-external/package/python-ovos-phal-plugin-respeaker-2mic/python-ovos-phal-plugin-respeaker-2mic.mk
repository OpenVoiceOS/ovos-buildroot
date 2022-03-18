################################################################################
#
# python-ovos-phal-plugin-respeaker-2mic
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_2MIC_VERSION = d8d2e2197b71332f8e6e88f6ccca8689ddd2ac8d
PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_2MIC_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-respeaker-2mic,$(PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_2MIC_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_2MIC_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_RESPEAKER_2MIC_LICENSE_FILES = LICENSE

$(eval $(python-package))
