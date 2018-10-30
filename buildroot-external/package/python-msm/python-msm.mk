################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.5.19
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/ee/ee/8e1dd6ceefea93e2c7009ad7d9b2fb9fcfacad8321042611a4f1179f3e86
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
