################################################################################
#
# python-ovos-phal-plugin-alsa
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION = 1ccbc7a6bfad49ba3b384d99b716aa22d266b1e4
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-alsa,$(PYTHON_OVOS_PHAL_PLUGIN_ALSA_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_ALSA_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_ALSA_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_ALSA_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
