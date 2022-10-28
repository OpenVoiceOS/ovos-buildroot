################################################################################
#
# python-convertdate
#
################################################################################

PYTHON_CONVERTDATE_VERSION = 2.4.0
PYTHON_CONVERTDATE_SOURCE = convertdate-$(PYTHON_CONVERTDATE_VERSION).tar.gz
PYTHON_CONVERTDATE_SITE = https://files.pythonhosted.org/packages/04/3d/04148ceb732dfb6f10e9b89fa5915080a91e27fe28fd982c259bc4d29ced
PYTHON_CONVERTDATE_SETUP_TYPE = setuptools
PYTHON_CONVERTDATE_LICENSE = MIT
PYTHON_CONVERTDATE_LICENSE_FILES = LICENSE

$(eval $(python-package))
