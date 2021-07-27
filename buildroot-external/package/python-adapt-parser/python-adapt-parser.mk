################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.5.1
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/ea/f3/d1043da5dfe5b3cc5c02b0a62425d8d7231a43214ddbb6f20459b6be491c
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
