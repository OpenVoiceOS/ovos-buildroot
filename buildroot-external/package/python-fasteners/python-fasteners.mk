################################################################################
#
# python-fasteners
#
################################################################################

PYTHON_FASTENERS_VERSION = 0.16
PYTHON_FASTENERS_SOURCE = fasteners-$(PYTHON_FASTENERS_VERSION).tar.gz
PYTHON_FASTENERS_SITE = https://files.pythonhosted.org/packages/d1/8f/a6c06f9bce5691a40283e52b92ec1522d6863951e738a31b109bf6bf2002
PYTHON_FASTENERS_SETUP_TYPE = setuptools
PYTHON_FASTENERS_LICENSE = Apache-2.0
PYTHON_FASTENERS_LICENSE_FILES = LICENSE

$(eval $(python-package))
