################################################################################
#
# python-pyee
#
################################################################################

PYTHON_PYEE_VERSION = 7.0.1
PYTHON_PYEE_SOURCE = pyee-$(PYTHON_PYEE_VERSION).tar.gz
PYTHON_PYEE_SITE = https://files.pythonhosted.org/packages/de/b1/2cf38e5375194f5d041efe66406b8b8282dc37d41b6c98d5f87ec556cb5e
PYTHON_PYEE_SETUP_TYPE = distutils
PYTHON_PYEE_LICENSE = MIT

$(eval $(python-package))
