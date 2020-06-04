################################################################################
#
# python-pyxdg
#
################################################################################

PYTHON_PYXDG_VERSION = 0.26
PYTHON_PYXDG_SOURCE = pyxdg-$(PYTHON_PYXDG_VERSION).tar.gz
PYTHON_PYXDG_SITE = https://files.pythonhosted.org/packages/47/6e/311d5f22e2b76381719b5d0c6e9dc39cd33999adae67db71d7279a6d70f4
PYTHON_PYXDG_SETUP_TYPE = distutils

$(eval $(python-package))
