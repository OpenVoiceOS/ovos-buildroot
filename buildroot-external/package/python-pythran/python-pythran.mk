################################################################################
#
# python-pythran
#
################################################################################

PYTHON_PYTHRAN_VERSION = 0.10.0
PYTHON_PYTHRAN_SOURCE = pythran-$(PYTHON_PYTHRAN_VERSION).tar.gz
PYTHON_PYTHRAN_SITE = https://files.pythonhosted.org/packages/c4/92/94b344b88bb010186caa65e5730509b4a6d2b1ab59e512ea11a2cbbb36fc
PYTHON_PYTHRAN_SETUP_TYPE = setuptools
PYTHON_PYTHRAN_LICENSE = FIXME: please specify the exact BSD version
PYTHON_PYTHRAN_LICENSE_FILES = LICENSE docs/LICENSE.rst

$(eval $(python-package))
$(eval $(host-python-package))
