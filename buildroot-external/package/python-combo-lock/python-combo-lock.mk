################################################################################
#
# python-combo-lock
#
################################################################################

PYTHON_COMBO_LOCK_VERSION = 0.2.6
PYTHON_COMBO_LOCK_SOURCE = combo_lock-$(PYTHON_COMBO_LOCK_VERSION).tar.gz
PYTHON_COMBO_LOCK_SITE = https://files.pythonhosted.org/packages/47/79/83e327fc03dd89c7b954eb290d89e9dc639ea3f4d1939139d1cccc452b22
PYTHON_COMBO_LOCK_SETUP_TYPE = setuptools
PYTHON_COMBO_LOCK_LICENSE = apache-2.0

$(eval $(python-package))
