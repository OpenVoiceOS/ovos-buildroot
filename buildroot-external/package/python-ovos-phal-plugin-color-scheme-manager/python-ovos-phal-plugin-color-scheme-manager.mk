################################################################################
#
# python-ovos-phal-plugin-color-scheme-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION = b89e6436c7b826ea0e16d15b9b1ef53cd7e92cb9
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-color-scheme-manager,$(PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
