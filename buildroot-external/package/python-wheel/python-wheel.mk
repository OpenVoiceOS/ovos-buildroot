################################################################################
#
# python-wheel
#
################################################################################

PYTHON_WHEEL_VERSION = 0.37.0
PYTHON_WHEEL_SOURCE = wheel-$(PYTHON_WHEEL_VERSION).tar.gz
PYTHON_WHEEL_SITE = https://files.pythonhosted.org/packages/4e/be/8139f127b4db2f79c8b117c80af56a3078cc4824b5b94250c7f81a70e03b
PYTHON_WHEEL_SETUP_TYPE = setuptools

$(eval $(python-package))
