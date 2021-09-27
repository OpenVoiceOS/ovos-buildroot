################################################################################
#
# python-bitstruct
#
################################################################################

PYTHON_BITSTRUCT_VERSION = 8.11.1
PYTHON_BITSTRUCT_SOURCE = bitstruct-$(PYTHON_BITSTRUCT_VERSION).tar.gz
PYTHON_BITSTRUCT_SITE = https://files.pythonhosted.org/packages/95/33/9f094b5e32bc0927acf282199d35c384092dd73505c88fadb69292106eaf
PYTHON_BITSTRUCT_SETUP_TYPE = setuptools
PYTHON_BITSTRUCT_LICENSE = MIT
PYTHON_BITSTRUCT_LICENSE_FILES = LICENSE

$(eval $(python-package))
