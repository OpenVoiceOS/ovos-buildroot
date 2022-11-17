################################################################################
#
# python-ovos-phal-plugin-configuration-provider
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION = be34224c48a55a5796949e124758696e26fe1df4
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-configuration-provider,$(PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
