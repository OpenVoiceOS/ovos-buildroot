################################################################################
#
# python-zeroconf
#
################################################################################

PYTHON_ZEROCONF_VERSION = 0.21.1
PYTHON_ZEROCONF_SOURCE = zeroconf-$(PYTHON_ZEROCONF_VERSION).tar.gz
PYTHON_ZEROCONF_SITE = https://files.pythonhosted.org/packages/44/94/459e1fc9b5bfec4dfd7a48c563c47b5961153c78c2f145bb5bb73e722ba0
PYTHON_ZEROCONF_SETUP_TYPE = setuptools
PYTHON_ZEROCONF_LICENSE = LGPL-2.1
PYTHON_ZEROCONF_LICENSE_FILES = COPYING

$(eval $(python-package))
