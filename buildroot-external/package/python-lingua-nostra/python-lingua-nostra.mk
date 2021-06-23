################################################################################
#
# python-lingua-nostra
#
################################################################################

PYTHON_LINGUA_NOSTRA_VERSION = a92df402b4b3e796748cf25eeefea5e41617ee8b
PYTHON_LINGUA_NOSTRA_SITE = $(call github,HelloChatterbox,lingua-nostra,$(PYTHON_LINGUA_NOSTRA_VERSION))
PYTHON_LINGUA_NOSTRA_SETUP_TYPE = setuptools
PYTHON_LINGUA_NOSTRA_LICENSE = Apache-2.0
PYTHON_LINGUA_NOSTRA_LICENSE_FILES = LICENSE

$(eval $(python-package))
