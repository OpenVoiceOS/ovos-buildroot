################################################################################
#
# python-ua-parser
#
################################################################################

PYTHON_UA_PARSER_VERSION = 0.16.1
PYTHON_UA_PARSER_SOURCE = ua-parser-$(PYTHON_UA_PARSER_VERSION).tar.gz
PYTHON_UA_PARSER_SITE = https://files.pythonhosted.org/packages/ab/e0/6be7ec0f1d3a485126fcce33c34ff8c41745e5b5ad43e500037f30e40064
PYTHON_UA_PARSER_SETUP_TYPE = setuptools
PYTHON_UA_PARSER_LICENSE = Apache-2.0
PYTHON_UA_PARSER_LICENSE_FILES = ua_parser/LICENSE

$(eval $(python-package))
