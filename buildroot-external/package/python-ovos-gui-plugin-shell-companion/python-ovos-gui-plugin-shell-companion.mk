################################################################################
#
# python-ovos-gui-plugin-shell-companion
#
################################################################################

PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_VERSION = 0.0.1a6
#PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_SOURCE = ovos-gui-plugin-shell-companion-$(PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_VERSION).tar.gz
#PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_SITE = https://files.pythonhosted.org/packages/cb/17/c0706995c8a0a30e4648c96d088159bbec94b1e9da39011295f0e52d6a9c
PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_SITE = $(call github,OpenVoiceOS,ovos-gui-plugin-shell-companion,$(PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_VERSION))
PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_SETUP_TYPE = setuptools
PYTHON_OVOS_GUI_PLUGIN_SHELL_COMPANION_LICENSE_FILES = LICENSE
PYTHON_OVOS_GUI_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
