################################################################################
#
# python-ovos-listener
#
################################################################################

PYTHON_OVOS_LISTENER_VERSION = 768cd42d50ff7439c359d07a2dbba085a1e8b657
PYTHON_OVOS_LISTENER_SITE = $(call github,OpenVoiceOS,ovos-listener,$(PYTHON_OVOS_LISTENER_VERSION))
PYTHON_OVOS_LISTENER_SETUP_TYPE = setuptools
PYTHON_OVOS_LISTENER_LICENSE_FILES = LICENSE
PYTHON_OVOS_LISTENER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
