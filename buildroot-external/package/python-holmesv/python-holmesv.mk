################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 8426a01b9c462a7b6ce33e0036654eeb3f09bf5f
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
