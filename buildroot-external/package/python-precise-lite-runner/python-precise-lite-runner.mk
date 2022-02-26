################################################################################
#
# python-precise-lite-runner
#
################################################################################

PYTHON_PRECISE_LITE_RUNNER_VERSION = aafdcff2bab7a90cd32e1b9ac16daf4b38995bc6
PYTHON_PRECISE_LITE_RUNNER_SITE = $(call github,OpenVoiceOS,precise_lite_runner,$(PYTHON_PRECISE_LITE_RUNNER_VERSION))
PYTHON_PRECISE_LITE_RUNNER_SETUP_TYPE = setuptools
PYTHON_PRECISE_LITE_RUNNER_LICENSE = LICENSE

$(eval $(python-package))
