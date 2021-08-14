################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 119388531b1cd7b8c0d47b8c0083aa895da9faf0
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
