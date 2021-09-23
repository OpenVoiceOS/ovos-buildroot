################################################################################
#
# python-precise-lite-runner
#
################################################################################

PYTHON_PRECISE_LITE_RUNNER_VERSION = 0.3.3
PYTHON_PRECISE_LITE_RUNNER_SOURCE = precise_lite_runner-$(PYTHON_PRECISE_LITE_RUNNER_VERSION).tar.gz
PYTHON_PRECISE_LITE_RUNNER_SITE = https://files.pythonhosted.org/packages/71/26/d798214472cd32f8803520672270123a00dfb6f4c6bbd8a3752c9aa411c9
PYTHON_PRECISE_LITE_RUNNER_SETUP_TYPE = setuptools
PYTHON_PRECISE_LITE_RUNNER_LICENSE = 

$(eval $(python-package))
