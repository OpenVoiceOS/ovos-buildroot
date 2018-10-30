################################################################################
#
# python-adapt-parser
#
################################################################################

PYTHON_ADAPT_PARSER_VERSION = 0.3.0
PYTHON_ADAPT_PARSER_SOURCE = adapt-parser-$(PYTHON_ADAPT_PARSER_VERSION).tar.gz
PYTHON_ADAPT_PARSER_SITE = https://files.pythonhosted.org/packages/36/a4/3ef82c754a8fb079a98d0adb66be1e3dc7a42d6faafdf1f106924a48c352
PYTHON_ADAPT_PARSER_SETUP_TYPE = setuptools

$(eval $(python-package))
