################################################################################
#
# python-pyftdi
#
################################################################################

PYTHON_PYFTDI_VERSION = 0.55.0
PYTHON_PYFTDI_SOURCE = pyftdi-$(PYTHON_PYFTDI_VERSION).tar.gz
PYTHON_PYFTDI_SITE = https://files.pythonhosted.org/packages/da/db/b900789a154e32dba50f132a2a76837331801f8b521b7e1bcbb852b01a35
PYTHON_PYFTDI_SETUP_TYPE = setuptools
PYTHON_PYFTDI_LICENSE = FIXME: please specify the exact BSD version
PYTHON_PYFTDI_LICENSE_FILES = pyftdi/doc/license.rst

$(eval $(python-package))
