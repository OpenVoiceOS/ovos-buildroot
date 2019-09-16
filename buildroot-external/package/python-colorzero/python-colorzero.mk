################################################################################
#
# python-colorzero
#
################################################################################

PYTHON_COLORZERO_VERSION = 1.1
PYTHON_COLORZERO_SOURCE = colorzero-$(PYTHON_COLORZERO_VERSION).tar.gz
PYTHON_COLORZERO_SITE = https://files.pythonhosted.org/packages/08/0e/826b882db4da2970f53331969d66efc2da2071ffd9a8824601d0feff513d
PYTHON_COLORZERO_SETUP_TYPE = setuptools
PYTHON_COLORZERO_LICENSE = BSD-3-Clause
PYTHON_COLORZERO_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
