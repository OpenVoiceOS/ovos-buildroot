################################################################################
#
# python-convertdate
#
################################################################################

PYTHON_CONVERTDATE_VERSION = 2.2.0
PYTHON_CONVERTDATE_SOURCE = convertdate-$(PYTHON_CONVERTDATE_VERSION).tar.gz
PYTHON_CONVERTDATE_SITE = https://files.pythonhosted.org/packages/92/c1/1125eba52ce9bccf783f0640eaad39ffa6e4271dcf37d19438c2ef115233
PYTHON_CONVERTDATE_SETUP_TYPE = setuptools
PYTHON_CONVERTDATE_LICENSE = MIT
PYTHON_CONVERTDATE_LICENSE_FILES = LICENSE

$(eval $(python-package))
