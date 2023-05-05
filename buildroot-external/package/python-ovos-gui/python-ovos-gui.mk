################################################################################
#
# python-ovos-gui
#
################################################################################

PYTHON_OVOS_GUI_VERSION = 502dec01d0055c54998280ffaa76d5f54961173f
PYTHON_OVOS_GUI_SITE = $(call github,OpenVoiceOS,ovos-gui,$(PYTHON_OVOS_GUI_VERSION))
PYTHON_OVOS_GUI_SETUP_TYPE = setuptools
PYTHON_OVOS_GUI_LICENSE_FILES = LICENSE
PYTHON_OVOS_GUI_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
