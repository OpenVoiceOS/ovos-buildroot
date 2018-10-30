################################################################################
#
# python-pyee
#
################################################################################

PYTHON_PYEE_VERSION = 1.0.1
PYTHON_PYEE_SOURCE = pyee-$(PYTHON_PYEE_VERSION).tar.gz
PYTHON_PYEE_SITE = https://files.pythonhosted.org/packages/0b/94/6820b8b1a21ce4d6a1c807342ac35cf4d5fd89b94b3f12e10de3c34d5507
PYTHON_PYEE_SETUP_TYPE = distutils
PYTHON_PYEE_LICENSE = MIT

$(eval $(python-package))
$(eval $(host-python-package))
