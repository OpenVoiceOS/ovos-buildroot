################################################################################
#
# python-ovos-phal-plugin-alsa
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION = 681c07943b368d961f82ba0bf254a2db0327b8aa
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-alsa,$(PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_ALSA_LICENSE_FILES = LICENSE

$(eval $(python-package))
