################################################################################
#
# python-msm
#
################################################################################

PYTHON_MSM_VERSION = 825e910a555e1882999647d226a56734a7b75ea4
PYTHON_MSM_SITE = $(call github,MycroftAI,mycroft-skills-manager,$(PYTHON_MSM_VERSION))
PYTHON_MSM_SETUP_TYPE = setuptools
PYTHON_MSM_LICENSE = Apache-2.0
PYTHON_MSM_LICENSE_FILES = LICENSE

$(eval $(python-package))
