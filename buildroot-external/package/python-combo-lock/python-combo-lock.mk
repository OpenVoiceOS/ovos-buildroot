################################################################################
#
# python-combo-lock
#
################################################################################

PYTHON_COMBO_LOCK_VERSION = 0.0.1
PYTHON_COMBO_LOCK_SOURCE = combo_lock-$(PYTHON_COMBO_LOCK_VERSION).tar.gz
PYTHON_COMBO_LOCK_SITE = https://files.pythonhosted.org/packages/64/85/af22ffdcbb8c4f2a487e3afd23dfff8683defdd2da0dc1efbdd702fa9f4c
PYTHON_COMBO_LOCK_SETUP_TYPE = setuptools
PYTHON_COMBO_LOCK_LICENSE = apache-2.0

$(eval $(python-package))
