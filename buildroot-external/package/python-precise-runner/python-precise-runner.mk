################################################################################
#
# python-precise-runner
#
################################################################################

PYTHON_PRECISE_RUNNER_VERSION = 0.2.1
PYTHON_PRECISE_RUNNER_SOURCE = precise-runner-$(PYTHON_PRECISE_RUNNER_VERSION).tar.gz
PYTHON_PRECISE_RUNNER_SITE = https://files.pythonhosted.org/packages/4b/cc/860af14c0522568a2d50dd1be3358a8ee00aa432f11806dc3d44506467a0
PYTHON_PRECISE_RUNNER_SETUP_TYPE = setuptools

$(eval $(python-package))
