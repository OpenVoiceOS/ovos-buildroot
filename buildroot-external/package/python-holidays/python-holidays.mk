################################################################################
#
# python-holidays
#
################################################################################

PYTHON_HOLIDAYS_VERSION = 0.10.4
PYTHON_HOLIDAYS_SOURCE = holidays-$(PYTHON_HOLIDAYS_VERSION).tar.gz
PYTHON_HOLIDAYS_SITE = https://files.pythonhosted.org/packages/cc/14/a8a30bae14091984acd262526a258b1890c3ada0e5ae0da747e2b8f2b77d
PYTHON_HOLIDAYS_SETUP_TYPE = setuptools
PYTHON_HOLIDAYS_LICENSE = MIT
PYTHON_HOLIDAYS_LICENSE_FILES = LICENSE

$(eval $(python-package))
