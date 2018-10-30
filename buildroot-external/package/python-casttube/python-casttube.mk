################################################################################
#
# python-casttube
#
################################################################################

PYTHON_CASTTUBE_VERSION = 0.1.0
PYTHON_CASTTUBE_SOURCE = casttube-$(PYTHON_CASTTUBE_VERSION).tar.gz
PYTHON_CASTTUBE_SITE = https://files.pythonhosted.org/packages/a1/57/00f76daff3a80f3e84ec25ac25e982f1aca77df16174b900a1c2ec1d9af1
PYTHON_CASTTUBE_SETUP_TYPE = setuptools

$(eval $(python-package))
