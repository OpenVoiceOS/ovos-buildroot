################################################################################
#
# python-mock-msm
#
################################################################################

PYTHON_MOCK_MSM_VERSION = 13b4847f7c8cdf46a3d5f8b1ab8ca2ab4c088f7d
PYTHON_MOCK_MSM_SITE = $(call github,HelloChatterbox,mock-msm,$(PYTHON_MOCK_MSM_VERSION))
PYTHON_MOCK_MSM_SETUP_TYPE = setuptools
PYTHON_MOCK_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
