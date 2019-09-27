################################################################################
#
# python-gpiozero
#
################################################################################

PYTHON_GPIOZERO_VERSION = 1.4.1
PYTHON_GPIOZERO_SOURCE = gpiozero-$(PYTHON_GPIOZERO_VERSION).tar.gz
PYTHON_GPIOZERO_SITE = https://files.pythonhosted.org/packages/3b/50/377575ff8fbdb672c27869ce536813cafdd94f5e14b5bf377edabb8a8097
PYTHON_GPIOZERO_SETUP_TYPE = setuptools

$(eval $(python-package))
