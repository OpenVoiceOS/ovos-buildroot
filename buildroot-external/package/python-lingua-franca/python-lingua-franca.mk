################################################################################
#
# python-lingua-franca
#
################################################################################

PYTHON_LINGUA_FRANCA_VERSION = a45b9d12a2a8adace210055a38f432dd51e7456d
PYTHON_LINGUA_FRANCA_SITE = $(call github,MycroftAI,lingua-franca,$(PYTHON_LINGUA_FRANCA_VERSION))
PYTHON_LINGUA_FRANCA_SETUP_TYPE = setuptools
PYTHON_LINGUA_FRANCA_LICENSE = Apache-2.0
PYTHON_LINGUA_FRANCA_LICENSE_FILES = LICENSE

$(eval $(python-package))
