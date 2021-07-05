################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = b00142baf2ca9d7c076611bc7aeffdf2ede83916
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
