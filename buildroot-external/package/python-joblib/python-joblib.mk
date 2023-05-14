################################################################################
#
# python-joblib
#
################################################################################

PYTHON_JOBLIB_VERSION = 1.2.0
PYTHON_JOBLIB_SOURCE = joblib-$(PYTHON_JOBLIB_VERSION).tar.gz
PYTHON_JOBLIB_SITE = https://files.pythonhosted.org/packages/45/dd/a5435a6902d6315241c48a5343e6e6675b007e05d3738ed97a7a47864e53
PYTHON_JOBLIB_SETUP_TYPE = setuptools
PYTHON_JOBLIB_LICENSE = FIXME: please specify the exact BSD version
PYTHON_JOBLIB_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
