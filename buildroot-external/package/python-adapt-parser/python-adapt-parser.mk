################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 1.0.0
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/ff/97/236a8cf280b789a86a7e5b50d3602e189ecc9726ebbb5b3259bb43761b02
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
