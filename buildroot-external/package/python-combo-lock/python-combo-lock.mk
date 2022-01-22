################################################################################
#
# python-combo-lock
#
################################################################################

PYTHON_COMBO_LOCK_VERSION = 0.2.1
PYTHON_COMBO_LOCK_SOURCE = combo_lock-$(PYTHON_COMBO_LOCK_VERSION).tar.gz
PYTHON_COMBO_LOCK_SITE = https://files.pythonhosted.org/packages/6f/a4/2721af17a3649b6716410e9f6ee80dfcc296f17d762a35659e4655a017f6
PYTHON_COMBO_LOCK_SETUP_TYPE = setuptools
PYTHON_COMBO_LOCK_LICENSE = apache-2.0

$(eval $(python-package))
