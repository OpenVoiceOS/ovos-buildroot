################################################################################
#
# python-msk
#
################################################################################

PYTHON_MSK_VERSION = 0.3.14
PYTHON_MSK_SOURCE = msk-$(PYTHON_MSK_VERSION).tar.gz
PYTHON_MSK_SITE = https://files.pythonhosted.org/packages/ef/de/d21d7d7c59f54b02910da5f4e5b77af9c40f5477079bcdfd0170e5ed4517
PYTHON_MSK_SETUP_TYPE = setuptools

$(eval $(python-package))
