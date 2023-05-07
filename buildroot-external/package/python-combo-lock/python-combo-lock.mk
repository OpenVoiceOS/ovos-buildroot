################################################################################
#
# python-combo-lock
#
################################################################################

PYTHON_COMBO_LOCK_VERSION = 0.2.5
PYTHON_COMBO_LOCK_SOURCE = combo_lock-$(PYTHON_COMBO_LOCK_VERSION).tar.gz
PYTHON_COMBO_LOCK_SITE = https://files.pythonhosted.org/packages/1a/7d/22bc221fd33a0f72c84ff8c6f6b5f06533825c058fe29a57d12467344cb3
PYTHON_COMBO_LOCK_SETUP_TYPE = setuptools
PYTHON_COMBO_LOCK_LICENSE = apache-2.0

$(eval $(python-package))
