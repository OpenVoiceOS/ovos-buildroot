################################################################################
#
# python-coveralls
#
################################################################################

PYTHON_COVERALLS_VERSION = 1.5.0
PYTHON_COVERALLS_SOURCE = coveralls-$(PYTHON_COVERALLS_VERSION).tar.gz
PYTHON_COVERALLS_SITE = https://files.pythonhosted.org/packages/b4/2f/aa954703728177258a935b766004f7504b9a4ff8c8aec0adee3d311feec2
PYTHON_COVERALLS_SETUP_TYPE = setuptools
PYTHON_COVERALLS_LICENSE = MIT
PYTHON_COVERALLS_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
