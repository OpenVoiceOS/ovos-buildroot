################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.3.4
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/01/80/2a437b4b59ada21209a420e44d9597d13f3853df3f16040d3077e1a7976a
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
