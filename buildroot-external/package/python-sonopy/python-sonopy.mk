################################################################################
#
# python-sonopy
#
################################################################################

PYTHON_SONOPY_VERSION = 0.1.2
PYTHON_SONOPY_SOURCE = sonopy-$(PYTHON_SONOPY_VERSION).tar.gz
PYTHON_SONOPY_SITE = https://files.pythonhosted.org/packages/2b/4d/862855fb391bc30351f90d6c50ea913df9d18b0ae3b6b8ef3c7aa3ac976f
PYTHON_SONOPY_SETUP_TYPE = setuptools
PYTHON_SONOPY_LICENSE = 

$(eval $(python-package))
