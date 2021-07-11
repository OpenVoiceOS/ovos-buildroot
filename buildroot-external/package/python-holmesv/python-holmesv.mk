################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 65741c4ffc300f8bb9e376dcb42c8092ee42e72b
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
