################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 0.6.3
PYTHON_MSM_SOURCE = msm-$(PYTHON_MSM_VERSION).tar.gz
PYTHON_MSM_SITE = https://files.pythonhosted.org/packages/8d/07/7fd52f9c7690925d48fffea97ec594beee797a75afd1e082ffe7b90dd341
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
