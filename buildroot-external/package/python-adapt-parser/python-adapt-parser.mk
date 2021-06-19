################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.4.1
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/68/01/b14c1675cf281654485a15374a8ab7251426c07e7b9e7aa5553a9cf895b8
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
