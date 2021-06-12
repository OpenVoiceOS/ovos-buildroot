################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = 618e79c0cca108eaa83eb0f93812b31d13af0078
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
