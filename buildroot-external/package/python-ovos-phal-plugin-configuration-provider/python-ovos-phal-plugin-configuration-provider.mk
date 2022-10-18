################################################################################
#
# python-ovos-phal-plugin-configuration-provider
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION = 993cae6379aa70f3e5994b5f21c6b6bcb6078db8
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-configuration-provider,$(PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
