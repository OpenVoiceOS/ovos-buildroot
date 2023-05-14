################################################################################
#
# python-precise-lite-runner
#
################################################################################

PYTHON_PRECISE_LITE_RUNNER_VERSION = f3cd8c138a5ba1b52c947496768777a31de15722
PYTHON_PRECISE_LITE_RUNNER_SITE = $(call github,OpenVoiceOS,precise_lite_runner,$(PYTHON_PRECISE_LITE_RUNNER_VERSION))
PYTHON_PRECISE_LITE_RUNNER_SETUP_TYPE = setuptools
PYTHON_PRECISE_LITE_RUNNER_LICENSE = LICENSE

$(eval $(python-package))
