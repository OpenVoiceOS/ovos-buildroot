################################################################################
#
# python-ovos-phal-plugin-color-scheme-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION = dd8fa31e681b3cee03874790b376384aaa2ab2ef
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-color-scheme-manager,$(PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
