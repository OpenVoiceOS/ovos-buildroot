################################################################################
#
# python-inflect
#
################################################################################

PYTHON_INFLECT_VERSION = 5.3.0
PYTHON_INFLECT_SOURCE = inflect-$(PYTHON_INFLECT_VERSION).tar.gz
PYTHON_INFLECT_SITE = https://files.pythonhosted.org/packages/a8/da/0d51c307544f4cde8d5aeadc2ff6b4d51f8fcd768467f62013b16a8002b5
PYTHON_INFLECT_SETUP_TYPE = setuptools

$(eval $(python-package))
