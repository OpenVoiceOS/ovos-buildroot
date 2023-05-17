################################################################################
#
# python-ovos-listener
#
################################################################################

PYTHON_OVOS_LISTENER_VERSION = 9fa3f8667125d677316e21e4c37d1b9dae2053d2
PYTHON_OVOS_LISTENER_SITE = $(call github,OpenVoiceOS,ovos-listener,$(PYTHON_OVOS_LISTENER_VERSION))
PYTHON_OVOS_LISTENER_SETUP_TYPE = setuptools
PYTHON_OVOS_LISTENER_LICENSE_FILES = LICENSE
PYTHON_OVOS_LISTENER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
