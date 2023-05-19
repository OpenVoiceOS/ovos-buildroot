################################################################################
#
# python-ovos-bus-client
#
################################################################################

PYTHON_OVOS_BUS_CLIENT_VERSION = 6e10ca0aab69ffabce7f2de836de76042e41f638
PYTHON_OVOS_BUS_CLIENT_SITE = $(call github,OpenVoiceOS,ovos-bus-client,$(PYTHON_OVOS_BUS_CLIENT_VERSION))
PYTHON_OVOS_BUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BUS_CLIENT_LICENSE = Apache-2.0
PYTHON_OVOS_BUS_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_BUS_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
