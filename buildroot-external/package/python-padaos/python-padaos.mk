################################################################################
#
# python-padaos
#
################################################################################

PYTHON_PADAOS_VERSION = 0.1.9
PYTHON_PADAOS_SOURCE = padaos-$(PYTHON_PADAOS_VERSION).tar.gz
PYTHON_PADAOS_SITE = https://files.pythonhosted.org/packages/5d/d9/f1e366c164c551c79e988c43fa282aea6e671d7842e6f70164ae09ad6376
PYTHON_PADAOS_SETUP_TYPE = setuptools

$(eval $(python-package))
