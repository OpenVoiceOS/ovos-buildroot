################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.8.7
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/f3/51/f0be5edba5d9e7a31b0b11857bff1324916bd2dd209314b97e1eacbed766
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
