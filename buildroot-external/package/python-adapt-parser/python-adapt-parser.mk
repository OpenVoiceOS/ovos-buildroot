################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.3.7
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/9e/db/62eeafa9ad1c0c20d6dd27de9e684c21d90a58f574e55720dc6aae6764ba
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
