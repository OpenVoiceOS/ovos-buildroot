################################################################################
#
# python-pyee
#
################################################################################

PYTHON_PYEE_VERSION = 9.0.4
PYTHON_PYEE_SOURCE = pyee-$(PYTHON_PYEE_VERSION).tar.gz
PYTHON_PYEE_SITE = https://files.pythonhosted.org/packages/99/d0/32803671d5d9dc032c766ad6c0716db98fa9b2c6ad9ec544f04849e9d3c7
PYTHON_PYEE_SETUP_TYPE = distutils
PYTHON_PYEE_LICENSE = MIT
PYTHON_PYEE_DEPENDENCIES = host-python-pytest-runner

$(eval $(python-package))
