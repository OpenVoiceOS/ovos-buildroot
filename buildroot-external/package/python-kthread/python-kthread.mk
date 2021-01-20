################################################################################
#
# python-kthread
#
################################################################################

PYTHON_KTHREAD_VERSION = 0.2.2
PYTHON_KTHREAD_SOURCE = kthread-$(PYTHON_KTHREAD_VERSION).tar.gz
PYTHON_KTHREAD_SITE = https://files.pythonhosted.org/packages/cc/32/cf425dc4622888376ddac4ee8105bd4a90b18a291a69c63d7bb702cb79bd
PYTHON_KTHREAD_SETUP_TYPE = setuptools

$(eval $(python-package))
