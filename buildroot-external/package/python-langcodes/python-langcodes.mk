################################################################################
#
# python-langcodes
#
################################################################################

PYTHON_LANGCODES_VERSION = 3.3.0
PYTHON_LANGCODES_SOURCE = langcodes-$(PYTHON_LANGCODES_VERSION).tar.gz
PYTHON_LANGCODES_SITE = https://files.pythonhosted.org/packages/5f/ec/9955d772ecac0bdfb5d706d64f185ac68bd0d4092acdc2c5a1882c824369
PYTHON_LANGCODES_SETUP_TYPE = setuptools
PYTHON_LANGCODES_LICENSE = MIT
PYTHON_LANGCODES_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
