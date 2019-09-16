################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.3.3
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/d7/be/be6417e4b6c099dfdcfec8c512de1c1e11ba446e6c81f405bd313fc2d6b4
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
