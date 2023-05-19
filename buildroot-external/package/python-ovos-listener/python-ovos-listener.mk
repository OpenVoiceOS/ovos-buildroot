################################################################################
#
# python-ovos-listener
#
################################################################################

PYTHON_OVOS_LISTENER_VERSION = 2d6ba2b6dbfae1c48c1833079d4aa94fa5cf6af5
PYTHON_OVOS_LISTENER_SITE = $(call github,OpenVoiceOS,ovos-listener,$(PYTHON_OVOS_LISTENER_VERSION))
PYTHON_OVOS_LISTENER_SETUP_TYPE = setuptools
PYTHON_OVOS_LISTENER_LICENSE_FILES = LICENSE
PYTHON_OVOS_LISTENER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
