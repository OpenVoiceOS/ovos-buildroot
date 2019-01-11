################################################################################
#
# python-coveralls
#
################################################################################

PYTHON_COVERALLS_VERSION = 1.5.1
PYTHON_COVERALLS_SOURCE = coveralls-$(PYTHON_COVERALLS_VERSION).tar.gz
PYTHON_COVERALLS_SITE = https://files.pythonhosted.org/packages/d2/4a/d0966ab522988667a9f23886dcec5cc029f1eb9848843466fbd2bb7a37fb
PYTHON_COVERALLS_SETUP_TYPE = setuptools
PYTHON_COVERALLS_LICENSE = MIT
PYTHON_COVERALLS_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
