################################################################################
#
# python-lingua-franca
#
################################################################################

PYTHON_LINGUA_FRANCA_VERSION = 0adc4314c96afd935975c82dde3d453e0713de41
PYTHON_LINGUA_FRANCA_SITE = $(call github,MycroftAI,lingua-franca,$(PYTHON_LINGUA_FRANCA_VERSION))
PYTHON_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
