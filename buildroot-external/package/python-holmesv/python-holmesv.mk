################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 80ce1a4cb294a6943f067246c4c4e71da7bc6326
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
