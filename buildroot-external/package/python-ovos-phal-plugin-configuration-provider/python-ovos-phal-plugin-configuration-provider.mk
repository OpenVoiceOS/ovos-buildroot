################################################################################
#
# python-ovos-phal-plugin-configuration-provider
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION = ef33111a00d249080f3c21edaac5ea7bf1340a6e
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-configuration-provider,$(PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
