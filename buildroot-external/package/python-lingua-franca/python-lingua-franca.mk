################################################################################
#
# python-lingua-franca
#
################################################################################

PYTHON_LINGUA_FRANCA_VERSION = 481535b1e5c4e34cb95e47732ee278a891773720
PYTHON_LINGUA_FRANCA_SITE = $(call github,MycroftAI,lingua-franca,$(PYTHON_LINGUA_FRANCA_VERSION))
PYTHON_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
