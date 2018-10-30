################################################################################
#
# python-padaos
#
################################################################################

PYTHON_PADAOS_VERSION = 0.1.7
PYTHON_PADAOS_SOURCE = padaos-$(PYTHON_PADAOS_VERSION).tar.gz
PYTHON_PADAOS_SITE = https://files.pythonhosted.org/packages/35/e0/ec50c08c5e8c5e049be9f841dae766c570e600c36730888be6cf1d317266
PYTHON_PADAOS_SETUP_TYPE = setuptools

$(eval $(python-package))
