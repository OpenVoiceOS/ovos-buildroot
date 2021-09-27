################################################################################
#
# python-tbm-utils
#
################################################################################

PYTHON_TBM_UTILS_VERSION = 2.6.0
PYTHON_TBM_UTILS_SOURCE = tbm-utils-$(PYTHON_TBM_UTILS_VERSION).tar.gz
PYTHON_TBM_UTILS_SITE = https://files.pythonhosted.org/packages/9a/5e/2885c4f941d1d76f058994004d65c414ea74f354204670d3a2fc0288a049
PYTHON_TBM_UTILS_SETUP_TYPE = setuptools
PYTHON_TBM_UTILS_LICENSE = MIT
PYTHON_TBM_UTILS_LICENSE_FILES = LICENSE

$(eval $(python-package))
