################################################################################
#
# python-pymeeus
#
################################################################################

PYTHON_PYMEEUS_VERSION = 0.3.7
PYTHON_PYMEEUS_SOURCE = PyMeeus-$(PYTHON_PYMEEUS_VERSION).tar.gz
PYTHON_PYMEEUS_SITE = https://files.pythonhosted.org/packages/2c/30/47957d487fff94083bdd17247734c165f12b5ac39a3abd1aa476a93eea6e
PYTHON_PYMEEUS_SETUP_TYPE = setuptools
PYTHON_PYMEEUS_LICENSE = GPL-3.0
PYTHON_PYMEEUS_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
