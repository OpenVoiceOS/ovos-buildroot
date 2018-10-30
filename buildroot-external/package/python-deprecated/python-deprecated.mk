################################################################################
#
# python-deprecated
#
################################################################################

PYTHON_DEPRECATED_VERSION = 1.2.3
PYTHON_DEPRECATED_SOURCE = Deprecated-$(PYTHON_DEPRECATED_VERSION).tar.gz
PYTHON_DEPRECATED_SITE = https://files.pythonhosted.org/packages/e1/fc/c729448c32aa702bffbfc986973e5fa48873ed1512d0ba9a2ffb09bf73be
PYTHON_DEPRECATED_SETUP_TYPE = setuptools
PYTHON_DEPRECATED_LICENSE_FILES = LICENSE.txt doc/License.rst

$(eval $(python-package))
