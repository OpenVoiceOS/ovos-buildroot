################################################################################
#
# python-pytzdata
#
################################################################################

PYTHON_PYTZDATA_VERSION = 2020.1
PYTHON_PYTZDATA_SOURCE = pytzdata-$(PYTHON_PYTZDATA_VERSION).tar.gz
PYTHON_PYTZDATA_SITE = https://files.pythonhosted.org/packages/67/62/4c25435a7c2f9c7aef6800862d6c227fc4cd81e9f0beebc5549a49c8ed53
PYTHON_PYTZDATA_SETUP_TYPE = setuptools
PYTHON_PYTZDATA_LICENSE = MIT
PYTHON_PYTZDATA_LICENSE_FILES = LICENSE

$(eval $(python-package))
