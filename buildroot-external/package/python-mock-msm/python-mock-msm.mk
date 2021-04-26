################################################################################
#
# python-mock-msm
#
################################################################################

PYTHON_MOCK_MSM_VERSION = 8a2ffde324f857928cd9c69ec68e97e5e97a8a77
PYTHON_MOCK_MSM_SITE = $(call github,HelloChatterbox,mock-msm,$(PYTHON_MOCK_MSM_VERSION))
PYTHON_MOCK_MSM_SETUP_TYPE = setuptools
PYTHON_MOCK_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
