################################################################################
#
# python-ovos-phal-plugin-color-scheme-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION = 756abc7f6ea6acba3595668b20363cda40f1a470
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-color-scheme-manager,$(PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
