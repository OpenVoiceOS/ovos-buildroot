################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.8.3
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/d5/b5/a7b53d4fc7ccbca6fe41f19c26a61c4a67a38068fe823e571b3e3519eb4b
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
