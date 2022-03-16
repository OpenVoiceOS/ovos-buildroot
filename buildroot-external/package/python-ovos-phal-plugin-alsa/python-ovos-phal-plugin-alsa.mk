################################################################################
#
# python-ovos-phal-plugin-alsa
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION = dc4a09c8c53f136297bb7c5e0515ad56a77cb491
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-alsa,$(PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_ALSA_LICENSE_FILES = LICENSE

$(eval $(python-package))
