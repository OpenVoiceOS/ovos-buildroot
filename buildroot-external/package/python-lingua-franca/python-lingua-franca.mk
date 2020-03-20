################################################################################
#
# python-lingua-franca
#
################################################################################

PYTHON_LINGUA_FRANCA_VERSION = 0.2.0
PYTHON_LINGUA_FRANCA_SOURCE = lingua_franca-$(PYTHON_LINGUA_FRANCA_VERSION).tar.gz
PYTHON_LINGUA_FRANCA_SITE = https://files.pythonhosted.org/packages/9f/04/54b9cfd14011f61e3d91592354e2460a5d85506c8996f802c1b4c1f9c9ff
PYTHON_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
