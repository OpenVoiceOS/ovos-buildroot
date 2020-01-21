################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.8.5
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/91/a0/98d07b9c5b45fd2ec42fe202722f76bc3cab902ca371474eb3d9a82758e5
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
