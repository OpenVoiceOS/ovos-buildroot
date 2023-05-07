################################################################################
#
# python-astral
#
################################################################################

PYTHON_ASTRAL_VERSION = 3.2
PYTHON_ASTRAL_SOURCE = astral-$(PYTHON_ASTRAL_VERSION).tar.gz
PYTHON_ASTRAL_SITE = https://files.pythonhosted.org/packages/04/d1/1adbf06a38dc339e41a1666f6c7135924594c20fd46e060fb263248c564d
PYTHON_ASTRAL_DEPENDENCIES = host-python-pytz
PYTHON_ASTRAL_SETUP_TYPE = setuptools
PYTHON_ASTRAL_LICENSE = Apache-2.0
PYTHON_ASTRAL_LICENSE_FILES = LICENSE

$(eval $(python-package))
