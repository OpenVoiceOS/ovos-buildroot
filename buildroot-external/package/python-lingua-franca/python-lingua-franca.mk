################################################################################
#
# python-lingua-franca
#
################################################################################

PYTHON_LINGUA_FRANCA_VERSION = d3444bb6578326168c038e03f2124dfb871c2a52
PYTHON_LINGUA_FRANCA_SITE = $(call github,MycroftAI,lingua-franca,$(PYTHON_LINGUA_FRANCA_VERSION))
PYTHON_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
