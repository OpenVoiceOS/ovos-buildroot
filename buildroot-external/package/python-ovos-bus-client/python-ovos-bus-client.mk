################################################################################
#
# python-ovos-bus-client
#
################################################################################

PYTHON_OVOS_BUS_CLIENT_VERSION = 8821ec701b061eff7821c9f3cd1f9d4e60153dbd
PYTHON_OVOS_BUS_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-bus-client,$(PYTHON_OVOS_BUS_CLIENT_VERSION))
PYTHON_OVOS_BUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BUS_CLIENT_LICENSE = Apache-2.0
PYTHON_OVOS_BUS_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_BUS_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
