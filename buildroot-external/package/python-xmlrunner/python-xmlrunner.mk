################################################################################
#
# python-xmlrunner
#
################################################################################

PYTHON_XMLRUNNER_VERSION = 1.7.7
PYTHON_XMLRUNNER_SOURCE = xmlrunner-$(PYTHON_XMLRUNNER_VERSION).tar.gz
PYTHON_XMLRUNNER_SITE = https://files.pythonhosted.org/packages/57/c0/a19e29bc6038a56bb690549573af6ea11a9d2a5c07aff2e27ed308c2cab9
PYTHON_XMLRUNNER_SETUP_TYPE = setuptools

$(eval $(python-package))
