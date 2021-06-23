################################################################################
#
# python-memory-tempfile
#
################################################################################

PYTHON_MEMORY_TEMPFILE_VERSION = 2.2.3
PYTHON_MEMORY_TEMPFILE_SOURCE = memory-tempfile-$(PYTHON_MEMORY_TEMPFILE_VERSION).tar.gz
PYTHON_MEMORY_TEMPFILE_SITE = https://files.pythonhosted.org/packages/7c/da/588403f523b1dfc9f70891b21d70f3d0f23b8c56985ca60af6b99c2c9dfc
PYTHON_MEMORY_TEMPFILE_SETUP_TYPE = setuptools
PYTHON_MEMORY_TEMPFILE_LICENSE = MIT
PYTHON_MEMORY_TEMPFILE_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
