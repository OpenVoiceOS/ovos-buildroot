################################################################################
#
# python-pyee
#
################################################################################

PYTHON_PYEE_VERSION = 8.1.0
PYTHON_PYEE_SOURCE = pyee-$(PYTHON_PYEE_VERSION).tar.gz
PYTHON_PYEE_SITE = https://files.pythonhosted.org/packages/fd/f8/d1c597ce15f3fd32ebdec9695da97a1af6e102c1ad8f9de32db84b05986c
PYTHON_PYEE_SETUP_TYPE = distutils
PYTHON_PYEE_LICENSE = MIT

$(eval $(python-package))
