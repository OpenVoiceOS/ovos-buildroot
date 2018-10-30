################################################################################
#
# python-pep8
#
################################################################################

PYTHON_PEP8_VERSION = 1.7.0
PYTHON_PEP8_SOURCE = pep8-$(PYTHON_PEP8_VERSION).tar.gz
PYTHON_PEP8_SITE = https://files.pythonhosted.org/packages/3e/b5/1f717b85fbf5d43d81e3c603a7a2f64c9f1dabc69a1e7745bd394cc06404
PYTHON_PEP8_SETUP_TYPE = setuptools

$(eval $(python-package))
