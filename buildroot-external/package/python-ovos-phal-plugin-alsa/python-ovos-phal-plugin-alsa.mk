################################################################################
#
# python-ovos-phal-plugin-alsa
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION = 1b9fd98db53fd279bd48ffa86d985c4be9ca4329
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-alsa,$(PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_ALSA_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_ALSA_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
