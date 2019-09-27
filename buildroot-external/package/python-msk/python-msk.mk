################################################################################
#
# python-msk
#
################################################################################

PYTHON_MSK_VERSION = 0.3.13
PYTHON_MSK_SOURCE = msk-$(PYTHON_MSK_VERSION).tar.gz
PYTHON_MSK_SITE = https://files.pythonhosted.org/packages/28/51/8d2193b8f1471178149cdbcc1830b086e978f99598208cae2ba2741b2979
PYTHON_MSK_SETUP_TYPE = setuptools

$(eval $(python-package))
