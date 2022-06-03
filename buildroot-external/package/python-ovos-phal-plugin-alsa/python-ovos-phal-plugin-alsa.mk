################################################################################
#
# python-ovos-phal-plugin-alsa
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION = 349ac425c0adc8056b4fa5e628c66f29286e4aa0
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-alsa,$(PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_ALSA_LICENSE_FILES = LICENSE

$(eval $(python-package))
