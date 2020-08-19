################################################################################
#
# python-lingua-franca
#
################################################################################

PYTHON_LINGUA_FRANCA_VERSION = 507a07b528fd70831aaac7d1cb75263838b87dee
PYTHON_LINGUA_FRANCA_SITE = $(call github,MycroftAI,lingua-franca,$(PYTHON_LINGUA_FRANCA_VERSION))
PYTHON_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
