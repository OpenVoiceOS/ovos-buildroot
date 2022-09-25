################################################################################
#
# python-ovos-phal-plugin-configuration-provider
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION = 5906782c16a12611e1c8114630b7f19faa9f85f7
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-configuration-provider,$(PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_CONFIGURATION_PROVIDER_LICENSE_FILES = LICENSE

$(eval $(python-package))
