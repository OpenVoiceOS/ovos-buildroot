################################################################################
#
# python-fann2
#
################################################################################

PYTHON_FANN2_VERSION = 1.0.7
PYTHON_FANN2_SOURCE = fann2-$(PYTHON_FANN2_VERSION).tar.gz
PYTHON_FANN2_SITE = https://files.pythonhosted.org/packages/a9/a3/af368a683a04850aa1bf2e097f17781eb26e7e7c269ddcecfcec5f2e05a3
PYTHON_FANN2_SETUP_TYPE = setuptools
PYTHON_FANN2_AUTORECONF = yes
PYTHON_FANN2_DEPENDENCIES = host-swig
PYTHON_FANN2_LICENSE = 
PYTHON_FANN2_LICENSE_FILES = 

$(eval $(python-package))
