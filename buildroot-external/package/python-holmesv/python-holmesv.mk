################################################################################
#
# python-holmesv
#
################################################################################

PYTHON_HOLMESV_VERSION = e1fa2035304484850f61f1487515f98eae2cc047
PYTHON_HOLMESV_SITE = $(call github,HelloChatterbox,HolmesV,$(PYTHON_HOLMESV_VERSION))
PYTHON_HOLMESV_SETUP_TYPE = setuptools
PYTHON_HOLMESV_LICENSE_FILES = LICENSE

$(eval $(python-package))
