################################################################################
#
# python-ovos-bus-client
#
################################################################################

PYTHON_OVOS_BUS_CLIENT_VERSION = 0.0.9a22
PYTHON_OVOS_BUS_CLIENT_SOURCE = ovos-bus-client-$(PYTHON_OVOS_BUS_CLIENT_VERSION).tar.gz
PYTHON_OVOS_BUS_CLIENT_SITE = https://files.pythonhosted.org/packages/17/ca/64632caeffa51781822422bb5c0bcede075e5d8958dfb2fb3d490cf89376
PYTHON_OVOS_BUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_BUS_CLIENT_LICENSE = Apache-2.0
PYTHON_OVOS_BUS_CLIENT_LICENSE_FILES = LICENSE
PYTHON_OVOS_BUS_CLIENT_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
