################################################################################
#
# python-pytest-runner
#
################################################################################

PYTHON_PYTEST_RUNNER_VERSION = 5.3.1
PYTHON_PYTEST_RUNNER_SOURCE = pytest-runner-$(PYTHON_PYTEST_RUNNER_VERSION).tar.gz
PYTHON_PYTEST_RUNNER_SITE = https://files.pythonhosted.org/packages/2a/04/c3223812b3427ffa95110c5781eae7fe8bc3e9e1fe4e2328bee17b9e5820
PYTHON_PYTEST_RUNNER_SETUP_TYPE = setuptools
PYTHON_PYTEST_RUNNER_LICENSE = MIT
PYTHON_PYTEST_RUNNER_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))

