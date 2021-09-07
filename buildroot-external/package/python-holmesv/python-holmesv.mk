################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 3cc7a557be7b2d144a02e41678abd43fb1c73242
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
