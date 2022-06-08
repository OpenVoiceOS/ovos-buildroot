################################################################################
#
# python-ovos-phal-plugin-color-scheme-manager
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION = 77eda6f8552f6dabcfc2ef4a89087278e109e29c
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-color-scheme-manager,$(PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_COLOR_SCHEME_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
