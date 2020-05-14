################################################################################
#
# python-msk
#
################################################################################

PYTHON_MSK_VERSION = 0.3.15
PYTHON_MSK_SOURCE = msk-$(PYTHON_MSK_VERSION).tar.gz
PYTHON_MSK_SITE = https://files.pythonhosted.org/packages/8a/80/5bd3efb6affe84e9626f10cfa8edf5dd87dba1ce3d136e01c694cc1fe368
PYTHON_MSK_SETUP_TYPE = setuptools

$(eval $(python-package))
