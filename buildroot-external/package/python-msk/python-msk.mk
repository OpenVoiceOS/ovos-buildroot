################################################################################
#
# python-msk
#
################################################################################

PYTHON_MSK_VERSION = 0.3.11
PYTHON_MSK_SOURCE = msk-$(PYTHON_MSK_VERSION).tar.gz
PYTHON_MSK_SITE = https://files.pythonhosted.org/packages/6d/2d/561d58e16d456ee5ca79d6dff3fb053f56da4ad62832eccce82b61a65789
PYTHON_MSK_SETUP_TYPE = setuptools

$(eval $(python-package))
