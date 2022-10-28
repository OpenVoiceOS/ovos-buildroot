################################################################################
#
# python-pymeeus
#
################################################################################

PYTHON_PYMEEUS_VERSION = 0.5.11
PYTHON_PYMEEUS_SOURCE = PyMeeus-$(PYTHON_PYMEEUS_VERSION).tar.gz
PYTHON_PYMEEUS_SITE = https://files.pythonhosted.org/packages/c7/ff/0f0a0becf088281c6bc6c75b7d7c03a2481d486ef6cc7c8899bbcab0a88d
PYTHON_PYMEEUS_SETUP_TYPE = setuptools
PYTHON_PYMEEUS_LICENSE = GNU Lesser General Public License v3 (LGPLv3)
PYTHON_PYMEEUS_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
