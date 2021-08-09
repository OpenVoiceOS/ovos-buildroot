################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = d39cb7aa9cb5f8ada8f3675d8c77d13406d2bb6f
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
