################################################################################
#
# python-pyftdi
#
################################################################################

PYTHON_PYFTDI_VERSION = 0.54.0
PYTHON_PYFTDI_SOURCE = pyftdi-$(PYTHON_PYFTDI_VERSION).tar.gz
PYTHON_PYFTDI_SITE = https://files.pythonhosted.org/packages/49/a3/6cd09c0493662b285b2ba87a08b1378a5b13e5cab44eb6a3f740c801c804
PYTHON_PYFTDI_SETUP_TYPE = setuptools
PYTHON_PYFTDI_LICENSE = FIXME: please specify the exact BSD version
PYTHON_PYFTDI_LICENSE_FILES = pyftdi/doc/license.rst

$(eval $(python-package))
