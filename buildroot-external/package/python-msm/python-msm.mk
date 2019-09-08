################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.7.9
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/46/e7/cd1c3771ecf644d95ef7c3ce7b53eeccccac1ad57c3ca3211f70ad02be29
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
