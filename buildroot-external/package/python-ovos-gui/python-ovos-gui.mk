################################################################################
#
# python-ovos-gui
#
################################################################################

PYTHON_OVOS_GUI_VERSION = 0.1.0a2
PYTHON_OVOS_GUI_SOURCE = ovos-gui-$(PYTHON_OVOS_GUI_VERSION).tar.gz
PYTHON_OVOS_GUI_SITE = https://files.pythonhosted.org/packages/99/13/1dcfeb2a0a4f164d8f0467f0032dfc552b1f839da41998d7ab933af3ca3d
PYTHON_OVOS_GUI_SETUP_TYPE = setuptools
PYTHON_OVOS_GUI_LICENSE_FILES = LICENSE
PYTHON_OVOS_GUI_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
