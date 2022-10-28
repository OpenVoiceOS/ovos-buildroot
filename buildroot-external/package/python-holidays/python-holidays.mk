################################################################################
#
# python-holidays
#
################################################################################

PYTHON_HOLIDAYS_VERSION = 0.16
PYTHON_HOLIDAYS_SOURCE = holidays-$(PYTHON_HOLIDAYS_VERSION).tar.gz
PYTHON_HOLIDAYS_SITE = https://files.pythonhosted.org/packages/e9/64/d52bb3e440a2780af0ad8721526b3804f721df045357efd0778372e20489
PYTHON_HOLIDAYS_SETUP_TYPE = setuptools
PYTHON_HOLIDAYS_LICENSE = MIT
PYTHON_HOLIDAYS_LICENSE_FILES = LICENSE

$(eval $(python-package))
