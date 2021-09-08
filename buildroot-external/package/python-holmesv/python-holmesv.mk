################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = a12d3021391c0acae765a634120d47bae4742ac9
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
