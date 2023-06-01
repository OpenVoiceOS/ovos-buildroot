################################################################################
#
# python-scikit-build
#
################################################################################

PYTHON_SCIKIT_BUILD_VERSION = 0.17.5
PYTHON_SCIKIT_BUILD_SOURCE = scikit_build-$(PYTHON_SCIKIT_BUILD_VERSION).tar.gz
PYTHON_SCIKIT_BUILD_SITE = https://files.pythonhosted.org/packages/f8/23/a07369d9095648b61a302cd45c9661ef2d92fe546e0eb28a467c66c7c1d3
PYTHON_SCIKIT_BUILD_LICENSE = MIT
PYTHON_SCIKIT_BUILD_LICENSE_FILES = LICENSE
PYTHON_SCIKIT_BUILD_SETUP_TYPE = flit

$(eval $(host-python-package))
