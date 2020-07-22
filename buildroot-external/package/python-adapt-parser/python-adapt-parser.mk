################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.3.6
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/a9/dc/07eb7578b7c17ae9a3e2309a826f897211786881c705fb6c9f3fd3d03234
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
