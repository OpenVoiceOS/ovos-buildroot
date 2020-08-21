################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.8.8
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/7e/42/66f2d39be2767b064d0c384b764ef18aae11344e618287f40fea5c84c866
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
