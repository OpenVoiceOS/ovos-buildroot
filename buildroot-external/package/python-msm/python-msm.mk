################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.8.4
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/04/e0/e9522b675e72d1de6c3991b1cb7ecc0fbb53a3d625ba329db6f08bfa4de2
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
