################################################################################
#
# python-lingua-nostra
#
################################################################################

PYTHON_LINGUA_NOSTRA_VERSION = 83f0690977a1d8cc7f04e11bfded9ee3df7abd4b
PYTHON_LINGUA_NOSTRA_SITE = $(call github,HelloChatterbox,lingua-nostra,$(PYTHON_LINGUA_NOSTRA_VERSION))
PYTHON_LINGUA_NOSTRA_SETUP_TYPE = setuptools
PYTHON_LINGUA_NOSTRA_LICENSE = Apache-2.0
PYTHON_LINGUA_NOSTRA_LICENSE_FILES = LICENSE

$(eval $(python-package))
