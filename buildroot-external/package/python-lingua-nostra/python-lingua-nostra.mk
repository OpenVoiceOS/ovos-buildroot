################################################################################
#
# python-lingua-nostra
#
################################################################################

PYTHON_LINGUA_NOSTRA_VERSION = 3a8a691bda46c2644cd3bd5d5a5b37f3c36eed84
PYTHON_LINGUA_NOSTRA_SITE = $(call github,HelloChatterbox,lingua-nostra,$(PYTHON_LINGUA_NOSTRA_VERSION))
PYTHON_LINGUA_NOSTRA_SETUP_TYPE = setuptools
PYTHON_LINGUA_NOSTRA_LICENSE = Apache-2.0
PYTHON_LINGUA_NOSTRA_LICENSE_FILES = LICENSE

$(eval $(python-package))
