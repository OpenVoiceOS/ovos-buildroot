################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 916622e6c4607edcf71ffd451533387c04bc18df
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
